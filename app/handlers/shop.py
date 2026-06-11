from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.keyboards.main import cancel_payment_keyboard, main_menu_keyboard, products_keyboard
from app.models.order import Order
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
from app.utils.files import download_receipt_photo, format_rial
from app.utils.security import main_cb

router = Router()

_USERNAME_INPUT_RE = re.compile(r"^[a-zA-Z0-9_]{3,24}$")


def _payment_instructions(amount_text: str) -> str:
    return (
        f"💳 مبلغ قابل پرداخت: {amount_text}\n\n"
        f"شماره کارت:\n<code>{settings.PAYMENT_CARD_NUMBER}</code>\n\n"
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
        await callback.message.answer("فعلاً محصولی برای فروش تعریف نشده است.")
        await callback.answer()
        return

    await state.clear()
    await callback.message.answer(
        "🛒 یکی از سرویس‌های زیر را انتخاب کنید:",
        reply_markup=products_keyboard(products),
    )
    await callback.answer()


@router.callback_query(main_cb.filter(F.action == "select_product"))
async def on_select_product(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    user, error = await _require_verified_user(session, callback.from_user.id)
    if error:
        await callback.answer(error, show_alert=True)
        return

    data = main_cb.parse(callback.data or "")
    try:
        product_id = int(data.get("item_id", "0"))
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
    await state.set_state(ShopState.waiting_username)
    await state.update_data(product_id=product.id)

    duration_label = product.duration or f"{product.duration_days} روز"
    await callback.message.answer(
        f"📦 سرویس: {product.name}\n"
        f"⏱ مدت: {duration_label}\n"
        f"💰 قیمت: {product.price_label}\n\n"
        "👤 لطفاً نام کاربری دلخواه خود را وارد کنید:\n"
        "(فقط حروف انگلیسی، عدد و _ — ۳ تا ۲۴ کاراکتر)\n"
        "در صورت تکراری بودن، دو رقم تصادفی به انتهای آن اضافه می‌شود.",
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

    label = user_display_label(user, message.from_user.username)
    order = await create_purchase_order(
        session,
        telegram_id=message.from_user.id,
        user_label=label,
        product_id=product.id,
        product_name=product.name,
        amount_label=product.price_label,
        amount_rial=product.price_rial,
        requested_username=raw.lower(),
    )

    await state.set_state(ShopState.waiting_receipt)
    await state.update_data(order_id=order.id, product_id=None)

    duration_label = product.duration or f"{product.duration_days} روز"
    await message.answer(
        f"✅ نام کاربری ثبت شد: <code>{raw.lower()}</code>\n"
        f"📦 سرویس: {product.name}\n"
        f"⏱ مدت: {duration_label}\n\n"
        f"{_payment_instructions(product.price_label)}",
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
    await callback.message.answer(
        f"💰 مبلغ شارژ را به <b>تومان</b> وارد کنید (حداقل {format_rial(settings.MIN_TOPUP_RIAL)}):",
        parse_mode="HTML",
        reply_markup=cancel_payment_keyboard(),
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

    await message.answer(
        _payment_instructions(format_rial(amount)),
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
    await callback.message.answer("سفارش لغو شد.", reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(main_cb.filter(F.action == "back_menu"))
async def on_back_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("بازگشت به منو:", reply_markup=main_menu_keyboard())
    await callback.answer()
