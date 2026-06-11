# Production Deployment Audit Report

Generated during production hardening (2026-05-24).

| File | Issue Type | Risk | Recommendation | Status |
|------|------------|------|----------------|--------|
| `frontend/src/services/data.ts` | Mock/Demo Data | Critical | Remove file; use real API only | **Removed** |
| `frontend/src/services/api.ts` | Mock API Usage | Critical | Remove `useMockApi` branches | **Fixed** |
| `frontend/src/services/authService.ts` | Fake Services / Mock Login | Critical | API-only authentication | **Fixed** |
| `frontend/src/config/env.ts` | Dev Config (`useMockApi` default true) | Critical | Remove mock flags | **Fixed** |
| `frontend/src/pages/LoginPage.tsx` | Demo hint (mock credentials) | High | Remove UI hint | **Fixed** |
| `frontend/.env.example` | Mock admin credentials | Medium | Remove mock vars | **Fixed** |
| `backend/app/seed.py` | Seed/Demo Data (products, transactions, discounts) | Critical | Admin-only bootstrap | **Fixed** |
| `backend/app/services/dashboard_service.py` | Hardcoded `total_revenue = 5059980` | High | Compute from DB | **Fixed** |
| `backend/app/config.py` | Dev JWT default, weak admin defaults | High | Enforce in production | **Kept with validator** |
| `backend/.env.example` | Placeholder secrets | Medium | Document only | **Updated** |
| `.env.example` | Placeholder tokens/keys | Medium | Document only | **Updated** |
| `docker-compose.yml` | Hardcoded Postgres password | High | Use env in production compose | **Fixed in production compose** |
| `docker-compose.yml` | Public Postgres port 5432 | Medium | No public port in production | **Fixed in production compose** |
| `config.py` (bot) | Default payment card placeholder | Low | Empty default | **Fixed** |
| `backend/openapi/*.json` | OpenAPI examples (example.com, admin/admin) | Low | Reference specs only — not runtime | **No change** |
| `.tmp_marzban_openapi.json` | Temp download artifact | Low | Add to .gitignore | **In .dockerignore** |
| `backend/app/database/migrations.py` | Ad-hoc SQL migrations | Medium | Replace with Alembic | **Replaced by Alembic** |
| `backend/app/database.py` | `create_all` on startup | Medium | Alembic in entrypoint | **Removed from startup** |
| `bot.py` | `create_all` + SQLite migrations | Medium | Schema via Alembic only | **Fixed** |
| `backend/app/main.py` | OpenAPI/Docs in dev | Low | Disabled in production | **Already implemented** |

## Migration System (before)

- **Alembic:** not present
- **create_all:** used by backend `init_db()` and bot `create_database()`
- **Schema timing:** built at application startup

## Migration System (after)

- **Alembic:** `backend/alembic/` with revision `001_initial`
- **Deploy:** `docker-entrypoint.sh` runs `alembic upgrade head`
- **Updates:** `paycollection update` rebuilds containers (migrations run on backend start)
