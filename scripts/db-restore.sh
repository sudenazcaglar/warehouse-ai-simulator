#!/usr/bin/env bash

set -euo pipefail

BACKUP_FILE="${1:-}"

if [[ -z "${BACKUP_FILE}" ]]; then
  echo "Usage: ./scripts/db-restore.sh backups/warehouse_ai_YYYYMMDD_HHMMSS.sql"
  exit 1
fi

if [[ ! -f "${BACKUP_FILE}" ]]; then
  echo "ERROR: Backup file not found: ${BACKUP_FILE}"
  exit 1
fi

if [[ ! -s "${BACKUP_FILE}" ]]; then
  echo "ERROR: Backup file is empty: ${BACKUP_FILE}"
  exit 1
fi

echo "Restoring PostgreSQL backup..."
echo "Input: ${BACKUP_FILE}"

docker compose exec -T postgres psql \
  -U warehouse_user \
  -d warehouse_ai \
  < "${BACKUP_FILE}"

echo "Restore completed successfully."
