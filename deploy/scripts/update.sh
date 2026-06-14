#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${PAYCOLLECTION_HOME:-/opt/paycollection}"
COMPOSE_FILE="${INSTALL_DIR}/docker-compose.production.yml"
BACKUP_SCRIPT="${INSTALL_DIR}/deploy/scripts/backup.sh"
DOMAIN="$(grep -E '^DOMAIN=' "${INSTALL_DIR}/.env" 2>/dev/null | cut -d= -f2- || true)"

cd "${INSTALL_DIR}"

PREVIOUS_COMMIT="$(git rev-parse HEAD)"
ROLLBACK_MARKER="${INSTALL_DIR}/deploy/.last_good_commit"

echo "[update] Creating pre-update backup..."
bash "${BACKUP_SCRIPT}"

echo "[update] Pulling latest changes..."
git fetch origin
git pull --ff-only origin main || git pull --ff-only

echo "[update] Rebuilding images..."
docker compose -f "${COMPOSE_FILE}" build

echo "[update] Applying migrations and restarting..."
docker compose -f "${COMPOSE_FILE}" up -d

echo "[update] Waiting for health check..."
attempts=0
healthy=0
while [[ "${attempts}" -lt 60 ]]; do
  if docker compose -f "${COMPOSE_FILE}" exec -T backend curl -fsS http://127.0.0.1:8000/health/live >/dev/null 2>&1; then
    if [[ -n "${DOMAIN}" ]] && curl -fsSk "https://${DOMAIN}/health/live" >/dev/null 2>&1; then
      healthy=1
      break
    elif [[ -z "${DOMAIN}" ]]; then
      healthy=1
      break
    fi
  fi
  attempts=$((attempts + 1))
  sleep 3
done

if [[ "${healthy}" -ne 1 ]]; then
  echo "[update] Health check failed — rolling back to ${PREVIOUS_COMMIT}..."
  git checkout "${PREVIOUS_COMMIT}"
  docker compose -f "${COMPOSE_FILE}" build
  docker compose -f "${COMPOSE_FILE}" up -d
  echo "[update] Rollback completed. Investigate logs: docker compose -f ${COMPOSE_FILE} logs"
  exit 1
fi

echo "${PREVIOUS_COMMIT}" > "${ROLLBACK_MARKER}.previous"
git rev-parse HEAD > "${ROLLBACK_MARKER}"
echo "[update] Update successful."
