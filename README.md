# PayCollectionBOT

ربات تلگرام + پنل ادمین React + API FastAPI — استقرار Production با Docker.

## استقرار سریع (Production)

```bash
sudo bash install.sh
```

پس از نصب:

```bash
paycollection update    # بروزرسانی
paycollection backup    # پشتیبان‌گیری
```

مستندات کامل: **[DEPLOYMENT.md](DEPLOYMENT.md)**

## توسعه محلی

```bash
docker compose up -d          # PostgreSQL
cd backend && alembic upgrade head && uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
python bot.py
```

## ساختار

| پوشه | توضیح |
|------|--------|
| `app/` | ربات تلگرام (aiogram) |
| `backend/` | REST API (FastAPI + Alembic) |
| `frontend/` | پنل ادمین (React + Vite) |
| `deploy/` | Nginx, backup, update scripts |
| `install.sh` | نصب خودکار Production |
