#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${PAYCOLLECTION_HOME:-/opt/paycollection}"
COMPOSE_FILE="${INSTALL_DIR}/docker-compose.production.yml"

docker compose -f "${COMPOSE_FILE}" exec -T nginx nginx -t
docker compose -f "${COMPOSE_FILE}" exec -T nginx nginx -s reload
