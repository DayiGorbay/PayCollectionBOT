from __future__ import annotations

from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.main import back_menu_keyboard, main_menu_keyboard, products_keyboard
from app.keyboards.services import service_detail_keyboard, services_list_keyboard
from app.services.backend_client import delete_user_service_via_api
from app.services.product_service import get_product
from app.services.service_service import get_service, list_active_services, mark_service_deleted
from app.utils.callback_ui import edit_callback_message
from app.utils.qrcode_util import make_qr_png_bytes
from app.utils.security import ServiceCallback, main_cb, service_cb

router = Router()


@router.callback_query(main_cb.filter(F.action == "my_services"))
async def on_my_services(callback: CallbackQuery, session: AsyncSession) -> None:
    services = await list_active_services(session, callback.from_user.id)
    if not services:
        await edit_callback_message(
            callback,
            "شما هنوز سرویس فعالی ندارید.",
            reply_markup=back_menu_keyboard(),
        )
    else:
        await edit_callback_message(
            callback,
            "📋 سرویس‌های فعال شما:",
            reply_markup=services_list_keyboard(services),
        )
    await callback.answer()


def _service_detail_text(svc) -> str:
    expire = "—"
    if svc.expire_at:
        expire = svc.expire_at.astimezone(timezone.utc).strftime("%Y/%m/%d")
    return (
        f"👤 نام کاربری: <code>{svc.panel_username}</code>\n"
        f"🌐 حجم: {svc.data_gb} گیگابایت\n"
        f"📅 انقضا: {expire}\n"
        f"🖥 نوع پنل: {svc.panel_type}"
    )


async def _send_link_with_qr(callback: CallbackQuery, link: str, title: str) -> None:
    qr = BufferedInputFile(make_qr_png_bytes(link), filename="qr.png")
    await callback.message.answer_photo(
        photo=qr,
        caption=f"{title}\n\n<pre>{link}</pre>",
        parse_mode="HTML",
    )


@router.callback_query(service_cb.filter(F.action == "back_list"))
async def on_services_back_list(callback: CallbackQuery, session: AsyncSession) -> None:
    services = await list_active_services(session, callback.from_user.id)
    if not services:
        await edit_callback_message(
            callback,
            "سرویس فعالی ندارید.",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await edit_callback_message(
            callback,
            "📋 سرویس‌های فعال شما:",
            reply_markup=services_list_keyboard(services),
        )
    await callback.answer()


@router.callback_query(service_cb.filter(F.action == "view"))
async def on_service_view(
    callback: CallbackQuery,
    session: AsyncSession,
    callback_data: ServiceCallback,
) -> None:
    try:
        service_id = int(callback_data.service_id or "0")
    except ValueError:
        await callback.answer("سرویس نامعتبر است.", show_alert=True)
        return

    svc = await get_service(session, service_id, callback.from_user.id)
    if svc is None:
        await callback.answer("سرویس یافت نشد.", show_alert=True)
        return

    await edit_callback_message(
        callback,
        _service_detail_text(svc),
        reply_markup=service_detail_keyboard(svc.id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(service_cb.filter(F.action == "sub_link"))
async def on_service_sub_link(
    callback: CallbackQuery,
    session: AsyncSession,
    callback_data: ServiceCallback,
) -> None:
    try:
        service_id = int(callback_data.service_id or "0")
    except ValueError:
        await callback.answer("سرویس نامعتبر است.", show_alert=True)
        return

    svc = await get_service(session, service_id, callback.from_user.id)
    if not svc or not svc.subscription_url:
        await callback.answer("لینک سابسکریپشن موجود نیست.", show_alert=True)
        return
    await _send_link_with_qr(callback, svc.subscription_url, "🔗 لینک سابسکریپشن")
    await callback.answer()


@router.callback_query(service_cb.filter(F.action == "config_link"))
async def on_service_config_link(
    callback: CallbackQuery,
    session: AsyncSession,
    callback_data: ServiceCallback,
) -> None:
    try:
        service_id = int(callback_data.service_id or "0")
    except ValueError:
        await callback.answer("سرویس نامعتبر است.", show_alert=True)
        return

    svc = await get_service(session, service_id, callback.from_user.id)
    link = (svc.config_text if svc else None) or (svc.subscription_url if svc else None)
    if not svc or not link:
        await callback.answer("کانفیگ موجود نیست.", show_alert=True)
        return
    await _send_link_with_qr(callback, link, "⚙️ کانفیگ / لینک")
    await callback.answer()


@router.callback_query(service_cb.filter(F.action == "delete"))
async def on_service_delete(
    callback: CallbackQuery,
    session: AsyncSession,
    callback_data: ServiceCallback,
) -> None:
    try:
        service_id = int(callback_data.service_id or "0")
    except ValueError:
        await callback.answer("سرویس نامعتبر است.", show_alert=True)
        return

    svc = await get_service(session, service_id, callback.from_user.id)
    if svc is None:
        await callback.answer("سرویس یافت نشد.", show_alert=True)
        return

    try:
        await delete_user_service_via_api(svc.id, callback.from_user.id)
    except RuntimeError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    await mark_service_deleted(session, svc)
    await edit_callback_message(
        callback,
        "سرویس حذف شد.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(service_cb.filter(F.action == "renew"))
async def on_service_renew(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    callback_data: ServiceCallback,
) -> None:
    try:
        service_id = int(callback_data.service_id or "0")
    except ValueError:
        await callback.answer("سرویس نامعتبر است.", show_alert=True)
        return

    svc = await get_service(session, service_id, callback.from_user.id)
    if svc is None or not svc.product_id:
        await callback.answer("امکان تمدید این سرویس وجود ندارد.", show_alert=True)
        return

    product = await get_product(session, svc.product_id)
    if product is None:
        await callback.answer("محصول مرتبط یافت نشد.", show_alert=True)
        return

    await state.clear()
    await state.update_data(renew_product_id=product.id)
    await edit_callback_message(
        callback,
        f"🔄 برای تمدید «{product.name}»، همانند خرید جدید عمل کنید.\n"
        "از لیست محصولات انتخاب کنید:",
        reply_markup=products_keyboard([product]),
    )
    await callback.answer()
