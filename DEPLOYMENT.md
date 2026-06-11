# PayCollectionBOT — Production Deployment

Complete guide for deploying PayCollectionBOT on **Ubuntu 24.04+** using Docker.

## Architecture

```text
Internet (443/80)
        │
   nginx container  ──► frontend container (static React)
        │              backend container (FastAPI :8000)
        │              bot container (Telegram polling + :8090 health)
        └────────────► postgres container (internal network only)
```

All services are managed by `docker-compose.production.yml`. PostgreSQL is **not** exposed publicly.

### Components

| Container | Role |
|-----------|------|
| `paycollection-nginx` | Edge proxy, HTTPS, gzip, security headers |
| `paycollection-frontend` | Built React admin panel |
| `paycollection-backend` | REST API, JWT auth, Alembic migrations |
| `paycollection-bot` | Telegram bot (aiogram polling) |
| `paycollection-postgres` | PostgreSQL 16 persistent data |

### Persistent volumes

| Volume | Contents |
|--------|----------|
| `paycollection_pg_data` | PostgreSQL database |
| `paycollection_uploads` | Payment receipts & uploads |

---

## Requirements

- Ubuntu 24.04 LTS (or compatible)
- Root/sudo access
- Domain DNS A record pointing to server
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

---

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/DayiGorbay/PayCollectionBOT/main/install.sh -o install.sh
sudo bash install.sh
```

Or clone and run:

```bash
git clone https://github.com/DayiGorbay/PayCollectionBOT.git /opt/paycollection
cd /opt/paycollection
sudo bash install.sh
```

The installer will:

1. Install Docker, Certbot, UFW
2. Prompt for **Domain**, **Email**, **Bot Token**, **Admin Password**
3. Generate `JWT_SECRET_KEY`, `INTERNAL_API_KEY`, `POSTGRES_PASSWORD`
4. Build and start all containers
5. Obtain Let's Encrypt SSL certificate
6. Configure firewall (22, 80, 443)
7. Install `paycollection` CLI

Default install path: `/opt/paycollection`

---

## Environment Variables

See [`.env.production.example`](.env.production.example) for the full list.

| Variable | Description |
|----------|-------------|
| `DOMAIN` | Admin panel domain |
| `POSTGRES_PASSWORD` | Database password (auto-generated) |
| `JWT_SECRET_KEY` | JWT signing key (auto-generated) |
| `INTERNAL_API_KEY` | Bot ↔ API internal auth (auto-generated) |
| `BOT_TOKEN` | Telegram bot token |
| `BOT_PROXY_ENABLED` | `true` / `false` — optional proxy for Bot API |
| `BOT_PROXY_URL` | `socks5://user:pass@host:port` or `http://user:pass@host:port` |
| `ADMIN_PASSWORD` | Initial admin panel password |
| `CORS_ORIGINS` | `https://your-domain` |
| `TRUSTED_HOSTS` | Your domain |
| `BACKEND_API_URL` | `http://backend:8000/api/v1` (internal) |
| `BOT_HEALTH_URL` | `http://bot:8090/health` |
| `UPLOADS_DIR` | `/app/data/uploads/receipts` |
| `PAYMENT_CARD_NUMBER` | Card number shown to users |
| `CHANNEL_ID` | Force-join channel ID |

---

## CLI Commands

```bash
paycollection update          # Backup, pull, rebuild, health-check, rollback on failure
paycollection backup          # Backup DB + uploads
paycollection restore <file>  # Restore from archive
paycollection status          # Container status
paycollection logs [service]  # Tail logs (backend, bot, nginx, ...)
paycollection health          # Call /health endpoint
```

Set custom install path:

```bash
export PAYCOLLECTION_HOME=/opt/paycollection
```

---

## Update

```bash
paycollection update
```

This will:

1. Create a backup (`deploy/backups/paycollection_YYYYMMDD_HHMMSS.tar.gz`)
2. Pull latest code from GitHub
3. Rebuild Docker images
4. Restart services (migrations run automatically on backend start)
5. Run health checks
6. Roll back to previous Git commit if health check fails

---

## Backup

```bash
paycollection backup
```

Creates a compressed archive containing:

- PostgreSQL dump (`database.dump`)
- Uploads volume (`uploads.tar.gz`)
- Metadata (`meta.env`)

Backups are stored in `deploy/backups/`. The last 14 backups are kept.

---

## Restore

```bash
paycollection restore /opt/paycollection/deploy/backups/paycollection_20260524_120000.tar.gz
```

**Warning:** Restore replaces current database and uploads.

---

## Rollback

If `paycollection update` fails health checks, it automatically rolls back to the previous Git commit and rebuilds.

Manual rollback:

```bash
cd /opt/paycollection
git log --oneline -5
git checkout <previous-commit>
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d
```

Or restore from backup:

```bash
paycollection restore deploy/backups/paycollection_<timestamp>.tar.gz
```

---

## Health Check

```bash
curl https://your-domain.com/health
```

Response:

```json
{
  "status": "ok",
  "api": "ok",
  "database": { "ok": true, "error": null },
  "bot": { "ok": true, "error": null }
}
```

Bot container `/health` (internal) also verifies Telegram API connectivity (via proxy when enabled):

```json
{
  "status": "ok",
  "service": "bot",
  "telegram": { "ok": true, "username": "YourBot", "error": null },
  "proxy": { "enabled": true, "url": "socks5://user:***@host:1080", "ok": true }
}
```

Returns HTTP 503 if database or bot is unhealthy.

---

## SSL Renewal

Certbot renewal runs daily via cron. On renewal, nginx is restarted automatically.

Manual renewal:

```bash
certbot renew \
  --config-dir /opt/paycollection/deploy/certbot/conf \
  --work-dir /opt/paycollection/deploy/certbot/work \
  --logs-dir /opt/paycollection/deploy/certbot/logs
docker compose -f /opt/paycollection/docker-compose.production.yml restart nginx
```

---

## Migrations (Alembic)

Migrations run automatically when the backend container starts:

```bash
alembic upgrade head
```

Manual migration:

```bash
docker compose -f docker-compose.production.yml exec backend alembic upgrade head
```

Create new migration (development):

```bash
cd backend
alembic revision --autogenerate -m "describe change"
```

### Existing database (pre-Alembic)

If tables already exist from a previous install:

```bash
docker compose -f docker-compose.production.yml exec backend alembic stamp head
```

---

## Local Development

```bash
# Database only
docker compose up -d

# Backend
cd backend && pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Bot
pip install -r requirements.txt
python bot.py
```

---

## Security

- `ENVIRONMENT=production` disables `/docs` and `/openapi.json`
- JWT + bcrypt for admin auth
- Login rate limiting per IP
- CORS restricted to panel domain
- TrustedHost middleware in production
- Security headers on API and nginx
- No mock data or demo seeds in production
- Secrets generated by installer — never commit `.env`

---

## Troubleshooting

```bash
# All logs
docker compose -f docker-compose.production.yml logs -f

# Single service
paycollection logs backend

# Restart stack
docker compose -f /opt/paycollection/docker-compose.production.yml restart

# Check env
cat /opt/paycollection/.env
```

---

## Audit

See [deploy/AUDIT_REPORT.md](deploy/AUDIT_REPORT.md) for the full development-data audit and remediation status.
