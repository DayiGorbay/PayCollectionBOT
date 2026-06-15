#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_install

echo "[docker-update] Pulling base images and rebuilding..."
compose pull --ignore-buildable 2>/dev/null || true
compose build --pull
compose up -d
echo "[docker-update] Done."
