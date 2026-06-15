#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${PAYCOLLECTION_HOME:-/opt/paycollection}"
COMPOSE_FILE="${INSTALL_DIR}/docker-compose.production.yml"
ENV_FILE="${INSTALL_DIR}/.env"
SCRIPTS_DIR="${INSTALL_DIR}/deploy/scripts"
VERSION_FILE="${INSTALL_DIR}/deploy/VERSION"

compose() {
  docker compose -f "${COMPOSE_FILE}" "$@"
}

read_env() {
  local key="$1"
  grep -E "^${key}=" "${ENV_FILE}" 2>/dev/null | cut -d= -f2- || true
}

panel_version() {
  if [[ -f "${VERSION_FILE}" ]]; then
    tr -d '[:space:]' < "${VERSION_FILE}"
  else
    echo "v1.0.0"
  fi
}

service_state() {
  local service="$1"
  local state
  state="$(compose ps --format '{{.Service}} {{.State}}' 2>/dev/null | awk -v s="${service}" '$1 == s { print $2; exit }')"
  if [[ -z "${state}" ]]; then
    echo "Not Installed"
  elif [[ "${state}" == "running" ]]; then
    echo "Running"
  else
    echo "${state^}"
  fi
}

ssl_state() {
  local domain
  domain="$(read_env DOMAIN)"
  if [[ -z "${domain}" ]]; then
    echo "Unknown"
    return
  fi
  if [[ -f "${INSTALL_DIR}/deploy/certbot/conf/live/${domain}/fullchain.pem" ]]; then
    echo "Active"
  else
    echo "Inactive"
  fi
}

require_install() {
  if [[ ! -f "${COMPOSE_FILE}" ]]; then
    echo "PayCollection is not installed at ${INSTALL_DIR}." >&2
    exit 1
  fi
}

require_env() {
  require_install
  if [[ ! -f "${ENV_FILE}" ]]; then
    echo "Missing ${ENV_FILE}" >&2
    exit 1
  fi
}

update_env_var() {
  local key="$1"
  local value="$2"
  local file="${ENV_FILE}.tmp"
  if grep -q "^${key}=" "${ENV_FILE}"; then
    sed "s|^${key}=.*|${key}=${value}|" "${ENV_FILE}" > "${file}"
  else
    cp "${ENV_FILE}" "${file}"
    echo "${key}=${value}" >> "${file}"
  fi
  mv "${file}" "${ENV_FILE}"
  chmod 600 "${ENV_FILE}"
}
