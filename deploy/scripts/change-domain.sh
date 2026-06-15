#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_env

read -r -p "Enter new domain (e.g. panel.example.com): " NEW_DOMAIN
NEW_DOMAIN="$(echo "${NEW_DOMAIN}" | tr -d '[:space:]')"
if [[ -z "${NEW_DOMAIN}" ]]; then
  echo "Domain cannot be empty." >&2
  exit 1
fi

update_env_var "DOMAIN" "${NEW_DOMAIN}"
update_env_var "CORS_ORIGINS" "https://${NEW_DOMAIN}"
update_env_var "TRUSTED_HOSTS" "${NEW_DOMAIN},localhost,127.0.0.1,backend"

sed "s/__DOMAIN__/${NEW_DOMAIN//\//\\/}/g" \
  "${INSTALL_DIR}/deploy/nginx/production.conf.tpl" \
  > "${INSTALL_DIR}/deploy/nginx/active.conf"

echo "[change-domain] Updated to ${NEW_DOMAIN}. Restart services and renew SSL if needed."
bash "${SCRIPTS_DIR}/restart.sh"
