#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="${1:-.env}"

REQUIRED_KEYS=(
  "PROJECT_NAME"
  "ENVIRONMENT"
  "API_HOST"
  "API_PORT"
  "DASHBOARD_PORT"
  "POSTGRES_HOST"
  "POSTGRES_PORT"
  "POSTGRES_DB"
  "POSTGRES_USER"
  "POSTGRES_PASSWORD"
  "DATABASE_URL"
  "REDIS_HOST"
  "REDIS_PORT"
  "MINIO_ENDPOINT"
  "MINIO_ACCESS_KEY"
  "MINIO_SECRET_KEY"
  "MINIO_BUCKET"
  "STREAMING_MODE"
  "STREAM_HOST"
  "STREAM_PORT"
  "PROMETHEUS_PORT"
  "GRAFANA_PORT"
  "NGINX_PORT"
)

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "ERROR: ${ENV_FILE} file not found."
  echo "Create it with: cp .env.example .env"
  exit 1
fi

echo "Validating ${ENV_FILE}..."

missing_keys=()

for key in "${REQUIRED_KEYS[@]}"; do
  if ! grep -Eq "^${key}=.+" "${ENV_FILE}"; then
    missing_keys+=("${key}")
  fi
done

if [[ ${#missing_keys[@]} -gt 0 ]]; then
  echo "ERROR: Missing required environment variables:"
  for key in "${missing_keys[@]}"; do
    echo "  - ${key}"
  done
  exit 1
fi

if grep -Eq "^OPENAI_API_KEY=replace_me$" "${ENV_FILE}"; then
  echo "WARNING: OPENAI_API_KEY is still set to replace_me."
  echo "This is acceptable for Docker Phase 2, but must be updated before LLM integration."
fi

echo "Environment validation passed."
