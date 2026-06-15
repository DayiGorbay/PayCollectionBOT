from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.handlers.start import START_TEXT
from app.keyboards.main import (
    cancel_payment_keyboard,
    discounted_pay_keyboard,
    main_menu_keyboard,
    product_payment_keyboard,
    products_keyboard,
)
from app.models.order import Order
from app.services.backend_client import approve_order_via_api
from app.services.bot_config_service import get_payment_card_number
from app.services.discount_service import validate_discount_code
from app.services.order_service import (
    attach_receipt,
    cancel_pending_order,
    create_purchase_order,
    create_topup_order,
    get_pending_order,
    user_display_label,
)
from app.services.product_service import get_product, list_active_products
from app.services.user_service import get_user_by_telegram_id
from app.states.shop import ShopState
from app.utils.callback_ui import edit_callback_message
from app.utils.files import download_receipt_photo, format_rial
from app.utils.security import MainCallback, main_cb

router = Router()

_USERNAME_INPUT_RE = re.compile(r"^[a-zA-Z0-9_]{3,24}$")


def _payment_instructions(amount_text: str, card_number: str) -> str:
    return (
        f"💳 مبلغ قابل پرداخت: {amount_text}\n\n"
        f"شماره کارت:\n<code>{card_number}</code>\n\n"
        "پس از واریز، تصویر رسید کارت‌به‌کارت را در همین چت ارسال کنید.\n"
        "فقط یک عکس واضح از رسید بفرستید."
    )


async def _require_verified_user(session: AsyncSession, telegram_id: int):
    user = await get_user_by_telegram_id(session, telegram_id)
    if user is None:
        return None, "ابتدا با /start وارد شوید."
    if not user.verified or user.is_suspicious:
        return None, "برای خرید ابتدا حساب خود را با ارسال شماره تأیید کنید."
    return user, None


async def _notify_admin(bot, order_id: int, title: str, user_label: str, amount: str) -> None:
    if not settings.ADMIN_TELEGRAM_ID:
        return
    text = (
        f"🛎 سفارش جدید #{order_id}\n"
        f"نوع: {title}\n"
        f"کاربر: {user_label}\n"
        f"مبلغ: {amount}\n\n"
        "پنل ادمین → سفارش‌ها"
    )
    try:
        await bot.send_message(settings.ADMIN_TELEGRAM_ID, text)
    except Exception:
        pass


@router.callback_query(main_cb.filter(F.action == "buy_service"))
async def on_buy_service(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    user, error = await _require_verified_user(session, callback.from_user.id)
    if error:
        await callback.answer(error, show_alert=True)
        return

    pending = await get_pending_order(session, callback.from_user.id)
    if pending:
        await callback.answer("یک سفارش در انتظار دارید. ابتدا آن را تکمیل یا لغو کنید.", show_alert=True)
        return

    products = await list_active_products(session)
    if not products:
        await edit_callback_message(
            callback,
            "فعلاً محصولی برای فروش تعریف نشده است.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    await state.clear()
    await edit_callback_message(
        callback,
        "🛒 یکی از سرویس‌های زیر را انتخاب کنید:",
        reply_markup=products_keyboard(products),
    )
    await callback.answer()


@router.callback_query(main_cb.filter(F.action == "select_product"))
async def on_select_product(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    callback_data: MainCallback,
) -> None:
    user, error = await _require_verified_user(session, callback.from_user.id)
    if error:
        await callback.answer(error, show_alert=True)
        return

    try:
        product_id = int(callback_data.item_id or "0")
    except ValueError:
        await callback.answer("محصول نامعتبر است.", show_alert=True)
        return

    product = await get_product(session, product_id)
    if product is None:
        await callback.answer("محصول یافت نشد.", show_alert=True)
        return

    pending = await get_pending_order(session, callback.from_user.id)
    if pending:
        await cancel_pending_order(session, pending)

    await state.clear()
    await state.update_data(product_id=product.id, discount_code=None, discount_amount_rial=0)

    duration_label = product.duration or f"{product.duration_days} روز"
    await edit_callback_message(
        callback,
        f"📦 سرویس: {product.name}\n"
        f"⏱ مدت: {duration_label}\n"
        f"💰 قیمت: {product.price_label}\n\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=product_payment_keyboard(product.id),
    )
    await callback.answer()


@router.callback_query(main_cb.filter(F.action == "apply_discount"))
async def on_apply_discount(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    callback_data: MainCallback,
) -> None:
    user, error = await _require_verified_user(session, callback.from_user.id)
    if error:
        await callback.answer(error, show_alert=True)
        return

    try:
        product_id = int(callback_data.item_id or "0")
    except ValueError:
        await callback.answer("محصول نامعتبر است.", show_alert=True)
        return

    product = await get_product(session, product_id)
    if product is None:
        await callback.answer("محصول یافت نشد.", show_alert=True)
        return

    await state.update_data(product_id=product.id)
    await state.set_state(ShopState.waiting_discount_code)
    await edit_callback_message(callback, "🏷 کد تخفیف خود را ارسال کنید:")
    await callback.answer()


@router.message(ShopState.waiting_discount_code, F.text)
async def on_discount_code_entered(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    product_id = data.get("product_id")
    if not product_id:
        await message.answer("سفارش منقضی شد. از منو دوباره شروع کنید.")
        await state.clear()
        return

    product = await get_product(session, int(product_id))
    if product is None:
        await message.answer("محصول یافت نشد.")
        await state.clear()
        return

    try:
        row, discount_rial = await validate_discount_code(session, message.text or "", product.price_rial)
    except ValueError as exc:
        await message.answer(str(exc))
        return

    final_price = product.price_rial - discount_rial
    await state.update_data(
        discount_code=row.code,
        discount_amount_rial=discount_rial,
        discount_row_id=row.id,
    )
    await state.set_state(None)

    await message.answer(
        f"✅ کد تخفیف «{row.code}» اعمال شد.\n"
        f"💰 مبلغ قبلی: {product.price_label}\n"
        f"🎁 تخفیف: {format_rial(discount_rial)}\n"
        f"💳 مبلغ نهایی: {format_rial(final_price)}\n\n"
        "برای ادامه خرید روی پرداخت بزنید:",
        reply_markup=discounted_pay_keyboard(product.id),
    )


@router.callback_query(main_cb.filter(F.action == "pay_service"))
async def on_pay_service(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    callback_data: MainCallback,
) -> None:
    user, error = await _require_verified_user(session, callback.from_user.id)
    if error:
        await callback.answer(error, show_alert=True)
        return

    try:
        product_id = int(callback_data.item_id or "0")
    except ValueError:
        await callback.answer("محصول نامعتبر است.", show_alert=True)
        return

    product = await get_product(session, product_id)
    if product is None:
        await callback.answer("محصول یافت نشد.", show_alert=True)
        return

    data = await state.get_data()
    discount_amount = int(data.get("discount_amount_rial") or 0)
    discount_code = data.get("discount_code")
    final_price = product.price_rial - discount_amount

    await state.set_state(ShopState.waiting_username)
    await state.update_data(
        product_id=product.id,
        discount_code=discount_code,
        discount_amount_rial=discount_amount,
        final_price_rial=final_price,
    )

    duration_label = product.duration or f"{product.duration_days} روز"
    price_line = format_rial(final_price)
    if discount_amount:
        price_line += f" (با تخفیف {format_rial(discount_amount)})"

    await edit_callback_message(
        callback,
        f"📦 سرویس: {product.name}\n"
        f"⏱ مدت: {duration_label}\n"
        f"💰 مبلغ: {price_line}\n\n"
        "👤 لطفاً نام کاربری دلخواه خود را وارد کنید:\n"
        "(فقط حروف انگلیسی، عدد و _ — ۳ تا ۲۴ کاراکتر)",
        reply_markup=cancel_payment_keyboard(),
    )
    await callback.answer()


@router.message(ShopState.waiting_username, F.text)
async def on_purchase_username(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    user, error = await _require_verified_user(session, message.from_user.id)
    if error:
        await message.answer(error)
        await state.clear()
        return

    raw = (message.text or "").strip()
    if not _USERNAME_INPUT_RE.match(raw):
        await message.answer(
            "نام کاربری نامعتبر است. فقط a-z، A-Z، 0-9 و _ (۳ تا ۲۴ کاراکتر)."
        )
        return

    data = await state.get_data()
    product_id = data.get("product_id")
    if not product_id:
        await message.answer("سفارش منقضی شد. از منو دوباره خرید را شروع کنید.")
        await state.clear()
        return

    product = await get_product(session, int(product_id))
    if product is None:
        await message.answer("محصول یافت نشد.")
        await state.clear()
        return

    discount_amount = int(data.get("discount_amount_rial") or 0)
    discount_code = data.get("discount_code")
    final_price = int(data.get("final_price_rial") or (product.price_rial - discount_amount))

    wallet_balance = user.balance or 0
    wallet_used = min(wallet_balance, final_price)
    card_due = final_price - wallet_used

    label = user_display_label(user, message.from_user.username)

    if card_due <= 0:
        user.balance = wallet_balance - wallet_used
        order = await create_purchase_order(
            session,
            telegram_id=message.from_user.id,
            user_label=label,
            product_id=product.id,
            product_name=product.name,
            amount_label=format_rial(final_price),
            amount_rial=final_price,
            requested_username=raw.lower(),
            discount_code=discount_code,
            discount_amount_rial=discount_amount,
            wallet_paid_rial=wallet_used,
            method="کیف پول",
        )
        try:
            await approve_order_via_api(order.id)
        except RuntimeError as exc:
            user.balance = wallet_balance
            await session.commit()
            await message.answer(f"خطا در فعال‌سازی سرویس: {exc}")
            await state.clear()
            return
        await state.clear()
        await message.answer(
            f"✅ سرویس «{product.name}» با موفقیت از کیف پول فعال شد.\n"
            f"👤 نام کاربری: <code>{raw.lower()}</code>\n"
            f"💰 {format_rial(wallet_used)} از موجودی کسر شد.",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
        return

    if wallet_used > 0:
        user.balance = wallet_balance - wallet_used
        await session.commit()

    order = await create_purchase_order(
        session,
        telegram_id=message.from_user.id,
        user_label=label,
        product_id=product.id,
        product_name=product.name,
        amount_label=format_rial(final_price),
        amount_rial=final_price,
        requested_username=raw.lower(),
        discount_code=discount_code,
        discount_amount_rial=discount_amount,
        wallet_paid_rial=wallet_used,
        method="کیف پول + کارت" if wallet_used else "کارت به کارت",
    )

    await state.set_state(ShopState.waiting_receipt)
    await state.update_data(order_id=order.id, product_id=None)

    duration_label = product.duration or f"{product.duration_days} روز"
    wallet_note = ""
    if wallet_used:
        wallet_note = f"💼 از کیف پول: {format_rial(wallet_used)}\n"
    card_number = await get_payment_card_number(session)
    await message.answer(
        f"✅ نام کاربری ثبت شد: <code>{raw.lower()}</code>\n"
        f"📦 سرویس: {product.name}\n"
        f"⏱ مدت: {duration_label}\n"
        f"{wallet_note}"
        f"{_payment_instructions(format_rial(card_due), card_number)}",
        parse_mode="HTML",
        reply_markup=cancel_payment_keyboard(),
    )


@router.message(ShopState.waiting_username)
async def on_purchase_username_invalid(message: Message) -> None:
    await message.answer("لطفاً نام کاربری را به صورت متن انگلیسی ارسال کنید.")


@router.callback_query(main_cb.filter(F.action == "topup_balance"))
async def on_topup_balance(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    user, error = await _require_verified_user(session, callback.from_user.id)
    if error:
        await callback.answer(error, show_alert=True)
        return

    pending = await get_pending_order(session, callback.from_user.id)
    if pending:
        await callback.answer("یک سفارش در انتظار دارید.", show_alert=True)
        return

    await state.set_state(ShopState.waiting_topup_amount)
    await edit_callback_message(
        callback,
        f"💰 مبلغ شارژ را به <b>تومان</b> وارد کنید (حداقل {format_rial(settings.MIN_TOPUP_RIAL)}):",
        reply_markup=cancel_payment_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ShopState.waiting_topup_amount, F.text)
async def on_topup_amount(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    user, error = await _require_verified_user(session, message.from_user.id)
    if error:
        await message.answer(error)
        await state.clear()
        return

    digits = re.sub(r"\D", "", message.text or "")
    if not digits:
        await message.answer("لطفاً فقط عدد وارد کنید.")
        return

    amount = int(digits)
    if amount < settings.MIN_TOPUP_RIAL:
        await message.answer(f"حداقل مبلغ شارژ {format_rial(settings.MIN_TOPUP_RIAL)} است.")
        return

    label = user_display_label(user, message.from_user.username)
    order = await create_topup_order(
        session,
        telegram_id=message.from_user.id,
        user_label=label,
        amount_rial=amount,
    )

    await state.set_state(ShopState.waiting_receipt)
    await state.update_data(order_id=order.id)

    card_number = await get_payment_card_number(session)
    await message.answer(
        _payment_instructions(format_rial(amount), card_number),
        parse_mode="HTML",
        reply_markup=cancel_payment_keyboard(),
    )


@router.message(ShopState.waiting_receipt, F.photo)
async def on_receipt_photo(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    order_id = data.get("order_id")
    if not order_id:
        await message.answer("سفارش فعالی یافت نشد. از منو دوباره شروع کنید.")
        await state.clear()
        return

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None or order.telegram_user_id != message.from_user.id:
        await message.answer("سفارش یافت نشد.")
        await state.clear()
        return

    if order.status != "در انتظار":
        await message.answer("این سفارش قبلاً پردازش شده است.")
        await state.clear()
        return

    photo = message.photo[-1]
    receipt_path = await download_receipt_photo(message.bot, photo.file_id, order.id)
    await attach_receipt(session, order, receipt_path=receipt_path, receipt_file_id=photo.file_id)

    await state.clear()

    await message.answer(
        f"✅ رسید شما برای سفارش #{order.id} دریافت شد.\n"
        "لطفاً تا تأیید رسید توسط ادمین صبر کنید.",
        reply_markup=main_menu_keyboard(),
    )
    await _notify_admin(
        message.bot,
        order.id,
        "خرید سرویس" if order.order_type == "purchase" else "افزایش موجودی",
        order.user_label,
        order.amount,
    )


@router.message(ShopState.waiting_receipt)
async def on_receipt_invalid(message: Message) -> None:
    await message.answer("لطفاً تصویر رسید پرداخت را به صورت عکس ارسال کنید.")


@router.callback_query(main_cb.filter(F.action == "cancel_payment"))
async def on_cancel_payment(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    order_id = data.get("order_id")
    if order_id:
        result = await session.execute(
            select(Order).where(Order.id == order_id, Order.telegram_user_id == callback.from_user.id)
        )
        order = result.scalar_one_or_none()
        if order and order.status == "در انتظار":
            await cancel_pending_order(session, order)

    await state.clear()
    await edit_callback_message(
        callback,
        "سفارش لغو شد.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(main_cb.filter(F.action == "back_menu"))
async def on_back_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await edit_callback_message(callback, START_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()
