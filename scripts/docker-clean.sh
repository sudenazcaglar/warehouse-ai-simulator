#!/usr/bin/env bash

set -euo pipefail

echo "Stopping containers..."
docker compose down

echo "Removing dangling Docker resources..."
docker system prune -f

echo "Docker cleanup completed."
