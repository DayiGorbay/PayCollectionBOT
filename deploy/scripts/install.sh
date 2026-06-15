#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${PAYCOLLECTION_HOME:-/opt/paycollection}"
INSTALLER="${INSTALL_DIR}/install.sh"

if [[ -f "${INSTALLER}" ]]; then
  exec bash "${INSTALLER}" "$@"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_INSTALLER="$(cd "${SCRIPT_DIR}/../.." && pwd)/install.sh"

if [[ -f "${ROOT_INSTALLER}" ]]; then
  exec bash "${ROOT_INSTALLER}" "$@"
fi

echo "Install script not found. Clone the repository to ${INSTALL_DIR} first." >&2
exit 1
