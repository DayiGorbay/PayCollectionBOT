#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

read -r -p "This will remove PayCollection containers and volumes. Continue? (y/n): " answer
[[ "${answer}" =~ ^[Yy]$ ]] || exit 0

if [[ -f "${COMPOSE_FILE}" ]]; then
  echo "[uninstall] Stopping and removing containers..."
  compose down -v --remove-orphans || true
fi

if [[ -d "${INSTALL_DIR}" ]]; then
  read -r -p "Delete installation directory ${INSTALL_DIR}? (y/n): " del
  if [[ "${del}" =~ ^[Yy]$ ]]; then
    rm -rf "${INSTALL_DIR}"
    echo "[uninstall] Removed ${INSTALL_DIR}"
  fi
fi

if [[ -f /usr/local/bin/paycollection ]]; then
  rm -f /usr/local/bin/paycollection
  echo "[uninstall] Removed /usr/local/bin/paycollection"
fi

echo "[uninstall] Done."
