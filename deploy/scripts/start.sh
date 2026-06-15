#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_install

echo "[start] Starting PayCollection services..."
compose up -d
echo "[start] Done."
