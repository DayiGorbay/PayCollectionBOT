#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_env

update_env_var "BOT_PROXY_ENABLED" "false"
update_env_var "BOT_PROXY_URL" ""
echo "[telegram-proxy] Proxy disabled. Restarting bot..."
compose up -d bot
echo "[telegram-proxy] Done."
