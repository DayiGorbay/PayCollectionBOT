# PayCollection Backend (FastAPI)

REST API امن برای پنل ادمین — پل بین **ربات تلگرام** و **فرانت React**.

## پیش‌نیاز

- Python 3.11+
- PostgreSQL 16 (یا `docker compose up -d` از ریشه پروژه)

## راه‌اندازی سریع

```bash
# 1) دیتابیس
docker compose up -d

# 2) بک‌اند
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # مقادیر را ویرایش کنید

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## اتصال فرانت

در `frontend/.env`:

```env
VITE_API_BASE_URL=/api/v1
VITE_USE_MOCK_API=false
VITE_API_PROXY_TARGET=http://127.0.0.1:8000
```

سپس `npm run dev` — Vite درخواست‌ها را به API پروکسی می‌کند.

## اتصال ربات

در `.env` ریشه پروژه همان `DATABASE_URL` PostgreSQL را تنظیم کنید:

```env
DATABASE_URL=postgresql+asyncpg://paycollection:paycollection@127.0.0.1:5432/paycollection
```

ربات و API روی **یک دیتابیس** کار می‌کنند (جدول `users` مشترک).

## امنیت

| لایه | توضیح |
|------|--------|
| JWT | توکن کوتاه‌عمر، Bearer در هدر |
| bcrypt | هش رمز ادمین |
| Rate limit | محدودیت تلاش ورود per IP |
| Account lock | قفل موقت بعد از تلاش‌های ناموفق |
| CORS | فقط originهای مجاز |
| Security headers | nosniff, DENY frame, HSTS در production |
| TrustedHost | در production |
| Internal API key | اختیاری برای فراخوانی داخلی ربات |

## Endpoints

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/users` — از جدول کاربران تلگرام
- `GET /api/v1/orders`, `/products`, `/transactions`, `/panels`, `/discounts`, `/settings`

Docs (فقط development): http://127.0.0.1:8000/docs
