#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${PAYCOLLECTION_HOME:-/opt/paycollection}"
COMPOSE_FILE="${INSTALL_DIR}/docker-compose.production.yml"
BACKUP_DIR="${INSTALL_DIR}/deploy/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
ARCHIVE="${BACKUP_DIR}/paycollection_${TIMESTAMP}.tar.gz"

mkdir -p "${BACKUP_DIR}"

echo "[backup] Creating backup at ${ARCHIVE}..."

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

# PostgreSQL dump
docker compose -f "${COMPOSE_FILE}" exec -T postgres \
  pg_dump -U paycollection -d paycollection -F c > "${TMP_DIR}/database.dump"

# Uploads volume
docker compose -f "${COMPOSE_FILE}" run --rm \
  -v paycollection_uploads:/data:ro \
  -v "${TMP_DIR}:/backup" \
  alpine sh -c "cd /data && tar czf /backup/uploads.tar.gz ."

# Metadata
cat > "${TMP_DIR}/meta.env" <<EOF
TIMESTAMP=${TIMESTAMP}
GIT_COMMIT=$(git -C "${INSTALL_DIR}" rev-parse HEAD 2>/dev/null || echo unknown)
DOMAIN=$(grep -E '^DOMAIN=' "${INSTALL_DIR}/.env" | cut -d= -f2- || true)
EOF

tar -czf "${ARCHIVE}" -C "${TMP_DIR}" .
echo "[backup] Done: ${ARCHIVE}"

# Keep last 14 backups
ls -1t "${BACKUP_DIR}"/paycollection_*.tar.gz 2>/dev/null | tail -n +15 | xargs -r rm -f
