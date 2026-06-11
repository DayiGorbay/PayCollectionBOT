#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: paycollection restore <backup-archive.tar.gz>" >&2
  exit 1
fi

ARCHIVE="$1"
INSTALL_DIR="${PAYCOLLECTION_HOME:-/opt/paycollection}"
COMPOSE_FILE="${INSTALL_DIR}/docker-compose.production.yml"

if [[ ! -f "${ARCHIVE}" ]]; then
  echo "Backup file not found: ${ARCHIVE}" >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

tar -xzf "${ARCHIVE}" -C "${TMP_DIR}"

echo "[restore] Stopping services..."
docker compose -f "${COMPOSE_FILE}" down

echo "[restore] Restoring PostgreSQL..."
docker compose -f "${COMPOSE_FILE}" up -d postgres
sleep 5
docker compose -f "${COMPOSE_FILE}" exec -T postgres \
  pg_restore -U paycollection -d paycollection --clean --if-exists < "${TMP_DIR}/database.dump" || true

echo "[restore] Restoring uploads..."
docker compose -f "${COMPOSE_FILE}" run --rm \
  -v paycollection_uploads:/data \
  -v "${TMP_DIR}:/backup:ro" \
  alpine sh -c "rm -rf /data/* && tar xzf /backup/uploads.tar.gz -C /data"

echo "[restore] Starting all services..."
docker compose -f "${COMPOSE_FILE}" up -d

echo "[restore] Restore completed from ${ARCHIVE}"
