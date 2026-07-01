#!/usr/bin/env bash

set -euo pipefail

BACKUP_DIR="backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="${BACKUP_DIR}/warehouse_ai_${TIMESTAMP}.sql"

mkdir -p "${BACKUP_DIR}"

echo "Creating PostgreSQL backup..."
echo "Output: ${BACKUP_FILE}"

docker compose exec -T postgres pg_dump \
  -U warehouse_user \
  -d warehouse_ai \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  > "${BACKUP_FILE}"

if [[ ! -s "${BACKUP_FILE}" ]]; then
  echo "ERROR: Backup file was not created or is empty."
  exit 1
fi

echo "Backup completed successfully."
echo "${BACKUP_FILE}"
