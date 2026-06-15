#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

echo "=== System Information ==="
echo "Hostname   : $(hostname)"
echo "OS         : $(. /etc/os-release 2>/dev/null && echo "${PRETTY_NAME:-unknown}" || uname -s)"
echo "Kernel     : $(uname -r)"
echo "Arch       : $(uname -m)"
echo "Uptime     : $(uptime -p 2>/dev/null || uptime)"
echo "Install dir: ${INSTALL_DIR}"
echo "Version    : $(panel_version)"
echo

if command -v docker >/dev/null 2>&1; then
  echo "Docker     : $(docker --version)"
  echo "Compose    : $(docker compose version 2>/dev/null || echo 'n/a')"
fi

if [[ -f "${COMPOSE_FILE}" ]]; then
  echo
  echo "=== Service Status ==="
  compose ps 2>/dev/null || true
fi
