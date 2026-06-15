#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_install

SERVICE="${1:-}"
if [[ -n "${SERVICE}" ]]; then
  compose logs -f --tail=200 "${SERVICE}"
else
  compose logs -f --tail=200
fi
