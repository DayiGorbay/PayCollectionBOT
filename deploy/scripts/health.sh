#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_install

DOMAIN="$(read_env DOMAIN)"

if [[ -n "${DOMAIN}" ]]; then
  curl -fsS "https://${DOMAIN}/health" && echo
  curl -fsS "https://${DOMAIN}/health/live" && echo
else
  compose exec -T backend curl -fsS http://127.0.0.1:8000/health/live && echo
  compose exec -T bot curl -fsS http://127.0.0.1:8090/health && echo
fi
