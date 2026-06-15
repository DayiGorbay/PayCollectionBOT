#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_install

docker info 2>/dev/null | head -n 20 || true
echo
compose ps
echo
docker system df 2>/dev/null || true
