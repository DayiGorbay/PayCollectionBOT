# PayCollectionBOT

یک ربات تلگرام حرفه‌ای با Python، `aiogram 3`، `SQLAlchemy` و `SQLite/PostgreSQL`.

## ویژگی‌ها

- ساختار ماژولار و production-ready
- سیستم رفرال با لینک اختصاصی
- احراز هویت شماره ایران
- کپچا با FSM
- عضویت اجباری در کانال
- پنل کاربری با اطلاعات داینامیک
- لاگ‌گیری استاندارد و error handling
- سیستم ضدتقلب و نرخ‌گیری

## نصب

1. کپی فایل `.env.example` به `.env`
2. مقدار `BOT_TOKEN` و `CHANNEL_USERNAME` را تنظیم کنید
3. محیط مجازی بسازید:

```bash
python -m venv .venv
.venv\Scripts\activate
```

4. پکیج‌ها را نصب کنید:

```bash
pip install -r requirements.txt
```

## اجرای ربات

```bash
python bot.py
```

## پایگاه داده

به صورت پیش‌فرض از SQLite استفاده می‌شود. اگر بخواهید PostgreSQL استفاده کنید، مقدار `DATABASE_URL` را به شکل زیر تغییر دهید:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost/paycollectionbot
```

## ساختار پروژه

- `bot.py` - نقطه ورود اصلی
- `config.py` - تنظیمات محیطی
- `app/handlers/` - مدیریت پیام‌ها و callback ها
- `app/keyboards/` - ساخت کیبوردها
- `app/middlewares/` - middleware های rate limit و امنیت
- `app/services/` - منطق کسب‌وکار و دسترسی به دیتابیس
- `app/database/` - اتصال و Session
- `app/models/` - مدل SQLAlchemy
- `app/states/` - وضعیت‌های FSM
- `app/utils/` - ابزارهای کمکی

## توجه

- `CHANNEL_ID` باید آیدی کانال شما باشد (مثلا `-1001234567890`).
- `CHANNEL_LINK` باید نام کاربری یا آدرس کانال شما باشد (مثلا `@YourChannelUsername`).
- برای تست ربات داخل کانال، ربات باید ادمین کانال باشد تا بتواند وضعیت عضویت کاربران را بررسی کند.
