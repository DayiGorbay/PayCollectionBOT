#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_install

BACKUP_DIR="${INSTALL_DIR}/deploy/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
DUMP="${BACKUP_DIR}/database_${TIMESTAMP}.dump"

mkdir -p "${BACKUP_DIR}"

echo "[db-backup] Creating database dump at ${DUMP}..."
compose exec -T postgres pg_dump -U paycollection -d paycollection -F c > "${DUMP}"
echo "[db-backup] Done."
