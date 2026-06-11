from __future__ import annotations

from pathlib import Path

from aiogram import Bot

from app.config import settings


def ensure_uploads_dir() -> Path:
    path = Path(settings.UPLOADS_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def download_receipt_photo(bot: Bot, file_id: str, order_id: int) -> str:
    uploads = ensure_uploads_dir()
    destination = uploads / f"order_{order_id}.jpg"
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, destination=destination)
    return str(destination.resolve())


def format_rial(amount: int) -> str:
    return f"{amount:,}".replace(",", "،") + " تومان"
