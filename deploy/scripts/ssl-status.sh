#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_env

DOMAIN="$(read_env DOMAIN)"
CERT="${INSTALL_DIR}/deploy/certbot/conf/live/${DOMAIN}/fullchain.pem"

echo "Domain : ${DOMAIN:-—}"
if [[ -n "${DOMAIN}" && -f "${CERT}" ]]; then
  echo "Status : Active"
  openssl x509 -in "${CERT}" -noout -subject -dates 2>/dev/null || true
else
  echo "Status : Inactive"
fi
