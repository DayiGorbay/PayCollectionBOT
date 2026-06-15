#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_env

mask_secret() {
  local value="$1"
  local len="${#value}"
  if [[ "${len}" -le 4 ]]; then
    echo "****"
  else
    echo "${value:0:2}****${value: -2}"
  fi
}

echo "=== PayCollection Configuration ==="
echo "Install dir : ${INSTALL_DIR}"
echo "Version     : $(panel_version)"
echo

while IFS= read -r line || [[ -n "${line}" ]]; do
  [[ "${line}" =~ ^# ]] && continue
  [[ -z "${line}" ]] && continue
  key="${line%%=*}"
  value="${line#*=}"
  case "${key}" in
    POSTGRES_PASSWORD|JWT_SECRET_KEY|INTERNAL_API_KEY|BOT_TOKEN|ADMIN_PASSWORD)
      value="$(mask_secret "${value}")"
      ;;
  esac
  printf '%-24s %s\n' "${key}:" "${value}"
done < "${ENV_FILE}"
