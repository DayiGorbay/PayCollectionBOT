#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_env

DOMAIN="$(read_env DOMAIN)"
EMAIL="$(read_env EMAIL)"

if [[ -z "${DOMAIN}" ]]; then
  echo "DOMAIN is not set in ${ENV_FILE}" >&2
  exit 1
fi

if [[ -z "${EMAIL}" ]]; then
  EMAIL="admin@${DOMAIN}"
fi

certbot renew \
  --config-dir "${INSTALL_DIR}/deploy/certbot/conf" \
  --work-dir "${INSTALL_DIR}/deploy/certbot/work" \
  --logs-dir "${INSTALL_DIR}/deploy/certbot/logs" \
  --deploy-hook "${SCRIPTS_DIR}/certbot-renew-hook.sh"

echo "[ssl-renew] Certificate renewal completed."
