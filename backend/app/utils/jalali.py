from __future__ import annotations

from datetime import datetime

try:
    import jdatetime
except ImportError:  # pragma: no cover
    jdatetime = None


def format_jalali_datetime(value: datetime | None, *, with_time: bool = True) -> str:
    if value is None:
        return "—"
    dt = value
    if dt.tzinfo is not None:
        dt = dt.astimezone()
    if jdatetime is None:
        if with_time:
            return dt.strftime("%Y/%m/%d %H:%M")
        return dt.strftime("%Y/%m/%d")
    jdt = jdatetime.datetime.fromgregorian(datetime=dt)
    if with_time:
        return jdt.strftime("%Y/%m/%d %H:%M")
    return jdt.strftime("%Y/%m/%d")


def format_rial(value: int) -> str:
    return f"{value:,}".replace(",", "،") + " تومان"
