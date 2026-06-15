#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_env

rand_hex() {
  openssl rand -hex "$1"
}

JWT_SECRET_KEY="$(rand_hex 32)"
INTERNAL_API_KEY="$(rand_hex 32)"
POSTGRES_PASSWORD="$(rand_hex 16)"

update_env_var "JWT_SECRET_KEY" "${JWT_SECRET_KEY}"
update_env_var "INTERNAL_API_KEY" "${INTERNAL_API_KEY}"
update_env_var "POSTGRES_PASSWORD" "${POSTGRES_PASSWORD}"
update_env_var "DATABASE_URL" "postgresql+asyncpg://paycollection:${POSTGRES_PASSWORD}@postgres:5432/paycollection"

echo "[regenerate-secrets] Secrets regenerated."
echo "WARNING: PostgreSQL password changed — update postgres container and restart all services."
bash "${SCRIPTS_DIR}/restart.sh"
