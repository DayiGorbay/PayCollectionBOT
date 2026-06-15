from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.main import back_menu_keyboard, main_menu_keyboard, products_keyboard
from app.keyboards.services import service_detail_keyboard, services_list_keyboard
from app.services.backend_client import (
    delete_user_service_via_api,
    get_user_service_via_api,
    list_user_services_via_api,
)
from app.services.product_service import get_product
from app.utils.callback_ui import edit_callback_message
from app.utils.qrcode_util import make_qr_png_bytes
from app.utils.security import ServiceCallback, main_cb, service_cb

router = Router()


def _format_bytes(bytes_value: int | None) -> str:
    if bytes_value is None or bytes_value < 0:
        return "—"
    if bytes_value == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = min(int(bytes_value).bit_length() // 10, len(units) - 1) if bytes_value > 0 else 0
    while i < len(units) - 1 and bytes_value >= 1024 ** (i + 1):
        i += 1
    value = bytes_value / (1024**i)
    return f"{value:.1f} {units[i]}"


def _format_expire(value: str | None) -> str:
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y/%m/%d")
    except ValueError:
        return value


def _service_detail_text(detail: dict) -> str:
    days = detail.get("daysRemaining")
    days_line = f"{days} روز" if days is not None else "—"
    return (
        f"👤 نام کاربری: <code>{detail.get('marzbanUsername', '—')}</code>\n"
        f"📦 محصول: {detail.get('product') or '—'}\n"
        f"🖥 پنل: {detail.get('panel') or detail.get('panelType', '—')}\n"
        f"📊 وضعیت: {detail.get('panelUserStatus') or detail.get('status', '—')}\n"
        f"🌐 حجم کل: {_format_bytes(detail.get('dataLimitBytes'))}\n"
        f"📉 مصرف شده: {_format_bytes(detail.get('usedTrafficBytes'))}\n"
        f"📈 باقی‌مانده: {_format_bytes(detail.get('remainingTrafficBytes'))}\n"
        f"📅 انقضا: {_format_expire(detail.get('expireAt'))}\n"
        f"⏳ روزهای باقی: {days_line}\n"
        f"🟢 آنلاین: {detail.get('onlineStatus') or '—'}\n"
        f"🕐 آخرین اتصال: {_format_expire(detail.get('lastOnlineAt'))}"
    )


async def _send_link_with_qr(callback: CallbackQuery, link: str, title: str) -> None:
    qr = BufferedInputFile(make_qr_png_bytes(link), filename="qr.png")
    await callback.message.answer_photo(
        photo=qr,
        caption=f"{title}\n\n<pre>{link}</pre>",
        parse_mode="HTML",
    )


@router.callback_query(main_cb.filter(F.action == "my_services"))
async def on_my_services(callback: CallbackQuery) -> None:
    try:
        services = await list_user_services_via_api(callback.from_user.id)
    except RuntimeError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

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


@router.callback_query(service_cb.filter(F.action == "back_list"))
async def on_services_back_list(callback: CallbackQuery) -> None:
    try:
        services = await list_user_services_via_api(callback.from_user.id)
    except RuntimeError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

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
    callback_data: ServiceCallback,
) -> None:
    try:
        service_id = int(callback_data.service_id or "0")
    except ValueError:
        await callback.answer("سرویس نامعتبر است.", show_alert=True)
        return

    try:
        detail = await get_user_service_via_api(service_id, callback.from_user.id)
    except RuntimeError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    await edit_callback_message(
        callback,
        _service_detail_text(detail),
        reply_markup=service_detail_keyboard(service_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(service_cb.filter(F.action == "sub_link"))
async def on_service_sub_link(
    callback: CallbackQuery,
    callback_data: ServiceCallback,
) -> None:
    try:
        service_id = int(callback_data.service_id or "0")
    except ValueError:
        await callback.answer("سرویس نامعتبر است.", show_alert=True)
        return

    try:
        detail = await get_user_service_via_api(service_id, callback.from_user.id)
    except RuntimeError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    link = detail.get("subscriptionUrl")
    if not link:
        await callback.answer("لینک سابسکریپشن موجود نیست.", show_alert=True)
        return
    await _send_link_with_qr(callback, link, "🔗 لینک سابسکریپشن")
    await callback.answer()


@router.callback_query(service_cb.filter(F.action == "config_link"))
async def on_service_config_link(
    callback: CallbackQuery,
    callback_data: ServiceCallback,
) -> None:
    try:
        service_id = int(callback_data.service_id or "0")
    except ValueError:
        await callback.answer("سرویس نامعتبر است.", show_alert=True)
        return

    try:
        detail = await get_user_service_via_api(service_id, callback.from_user.id)
    except RuntimeError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    links = detail.get("links") or []
    link = detail.get("configText") or (links[0] if links else None) or detail.get("subscriptionUrl")
    if not link:
        await callback.answer("کانفیگ موجود نیست.", show_alert=True)
        return
    await _send_link_with_qr(callback, link, "⚙️ کانفیگ / لینک")
    await callback.answer()


@router.callback_query(service_cb.filter(F.action == "delete"))
async def on_service_delete(
    callback: CallbackQuery,
    callback_data: ServiceCallback,
) -> None:
    try:
        service_id = int(callback_data.service_id or "0")
    except ValueError:
        await callback.answer("سرویس نامعتبر است.", show_alert=True)
        return

    try:
        await delete_user_service_via_api(service_id, callback.from_user.id)
    except RuntimeError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

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

    try:
        detail = await get_user_service_via_api(service_id, callback.from_user.id)
    except RuntimeError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    product_id = detail.get("productId")
    if not product_id:
        await callback.answer("امکان تمدید این سرویس وجود ندارد.", show_alert=True)
        return

    product = await get_product(session, int(product_id))
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
