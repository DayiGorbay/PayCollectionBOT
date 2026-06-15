#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_env

CURRENT_URL="$(read_env BOT_PROXY_URL)"
CURRENT_ENABLED="$(read_env BOT_PROXY_ENABLED)"

echo "Current proxy enabled: ${CURRENT_ENABLED:-false}"
echo "Current proxy URL    : ${CURRENT_URL:-—}"
echo

read -r -p "Enable Telegram proxy? (y/n) [${CURRENT_ENABLED:-n}]: " ENABLE_ANS
ENABLE_ANS="${ENABLE_ANS:-${CURRENT_ENABLED:-n}}"

if [[ "${ENABLE_ANS}" =~ ^[Yy]$ ]]; then
  read -r -p "Proxy URL [${CURRENT_URL}]: " PROXY_URL
  PROXY_URL="${PROXY_URL:-${CURRENT_URL}}"
  PROXY_URL="$(echo "${PROXY_URL}" | tr -d '[:space:]')"
  if [[ -z "${PROXY_URL}" ]]; then
    echo "Proxy URL cannot be empty when proxy is enabled." >&2
    exit 1
  fi
  update_env_var "BOT_PROXY_ENABLED" "true"
  update_env_var "BOT_PROXY_URL" "${PROXY_URL}"
else
  update_env_var "BOT_PROXY_ENABLED" "false"
  update_env_var "BOT_PROXY_URL" ""
fi

echo "[telegram-proxy] Configuration saved. Restarting bot..."
compose up -d bot
echo "[telegram-proxy] Done."
