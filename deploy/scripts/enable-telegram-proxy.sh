#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_env

read -r -p "Enter proxy URL (socks5://user:pass@host:port or http://user:pass@host:port): " PROXY_URL
PROXY_URL="$(echo "${PROXY_URL}" | tr -d '[:space:]')"
if [[ -z "${PROXY_URL}" ]]; then
  echo "Proxy URL cannot be empty." >&2
  exit 1
fi

update_env_var "BOT_PROXY_ENABLED" "true"
update_env_var "BOT_PROXY_URL" "${PROXY_URL}"
echo "[telegram-proxy] Proxy enabled. Restarting bot..."
compose up -d bot
echo "[telegram-proxy] Done."
