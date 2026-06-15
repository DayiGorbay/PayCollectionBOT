#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_install

echo "[stop] Stopping PayCollection services..."
compose down
echo "[stop] Done."
