#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: paycollection db-restore <database.dump>" >&2
  exit 1
fi

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_install

DUMP="$1"
if [[ ! -f "${DUMP}" ]]; then
  echo "Dump file not found: ${DUMP}" >&2
  exit 1
fi

echo "[db-restore] Restoring database from ${DUMP}..."
compose up -d postgres
sleep 5
compose exec -T postgres pg_restore -U paycollection -d paycollection --clean --if-exists < "${DUMP}" || true
compose up -d
echo "[db-restore] Done."
