#!/usr/bin/env bash

set -euo pipefail

check_http() {
  local name="$1"
  local url="$2"

  echo "Checking ${name}: ${url}"

  if curl -fsS "${url}" >/dev/null; then
    echo "OK: ${name}"
  else
    echo "ERROR: ${name} is not healthy"
    exit 1
  fi
}

check_exec() {
  local name="$1"
  shift

  echo "Checking ${name}: $*"

  if "$@" >/dev/null; then
    echo "OK: ${name}"
  else
    echo "ERROR: ${name} is not healthy"
    exit 1
  fi
}

echo "Running core service verification..."

check_http "API health" "http://localhost:8000/health"
check_http "API metrics" "http://localhost:8000/metrics"
check_http "Dashboard" "http://localhost:3000"
check_http "Nginx API gateway" "http://localhost:8080/api/health"
check_http "MinIO health" "http://localhost:9000/minio/health/live"

check_exec "PostgreSQL" docker compose exec -T postgres pg_isready -U warehouse_user -d warehouse_ai
check_exec "Redis" docker compose exec -T redis redis-cli ping

echo "All core services are healthy."
