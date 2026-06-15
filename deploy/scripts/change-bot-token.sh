#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_env

read -r -p "Enter new Telegram bot token: " NEW_TOKEN
NEW_TOKEN="$(echo "${NEW_TOKEN}" | tr -d '[:space:]')"
if [[ -z "${NEW_TOKEN}" ]]; then
  echo "Bot token cannot be empty." >&2
  exit 1
fi

update_env_var "BOT_TOKEN" "${NEW_TOKEN}"
echo "[change-bot-token] Token updated. Restarting bot..."
compose up -d bot
echo "[change-bot-token] Done."
