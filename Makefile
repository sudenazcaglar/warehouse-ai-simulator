SHELL := /bin/bash

.DEFAULT_GOAL := help

DC := docker compose
DC_FULL := docker compose --profile observability --profile training
DC_OBS := docker compose --profile observability
DC_PROD := docker compose -f docker-compose.prod.yml
DC_PROD_OBS := docker compose -f docker-compose.prod.yml --profile observability

.PHONY: help
help:
	@echo "Warehouse AI Simulator - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make env              Create .env from .env.example if missing"
	@echo "  make validate-env     Validate required environment variables"
	@echo "  make doctor           Validate Docker, env, and compose config"
	@echo ""
	@echo "Development Docker:"
	@echo "  make build            Build full development environment"
	@echo "  make up               Start full development environment"
	@echo "  make up-core          Start lightweight core environment"
	@echo "  make up-full          Start full environment with observability and training tools"
	@echo "  make up-observability Start core environment with Prometheus and Grafana"
	@echo "  make down             Stop all development services"
	@echo "  make restart          Restart full development environment"
	@echo "  make ps               Show full development service status"
	@echo "  make ps-core          Show core service status"
	@echo "  make logs             Follow full development logs"
	@echo "  make clean            Stop services and prune dangling resources"
	@echo "  make reset            Stop services and remove development volumes"
	@echo ""
	@echo "Production-like Docker:"
	@echo "  make prod-config      Validate production compose config"
	@echo "  make prod-up          Start production-like services"
	@echo "  make prod-up-obs      Start production-like services with observability"
	@echo "  make prod-ps          Show production-like service status"
	@echo "  make prod-down        Stop production-like services"
	@echo ""
	@echo "Health:"
	@echo "  make health           Verify full development service health"
	@echo "  make health-core      Verify core development service health"
	@echo "  make api-health       Check API health endpoint"
	@echo ""
	@echo "Shells:"
	@echo "  make db-shell         Open PostgreSQL shell"
	@echo "  make redis-shell      Open Redis CLI"
	@echo "  make api-shell        Open API container shell"
	@echo ""
	@echo "Logs:"
	@echo "  make api-logs         Follow API logs"
	@echo "  make dashboard-logs   Follow dashboard logs"
	@echo "  make db-logs          Follow PostgreSQL logs"

.PHONY: env
env:
	@if [ ! -f .env ]; then cp .env.example .env && echo ".env created from .env.example"; else echo ".env already exists"; fi

.PHONY: validate-env
validate-env:
	@./scripts/validate-env.sh .env

.PHONY: doctor
doctor: env validate-env
	@echo "Checking Docker daemon..."
	@docker info >/dev/null
	@echo "Docker daemon is running."
	@echo "Checking Docker Compose configuration..."
	@$(DC_FULL) config >/dev/null
	@echo "Docker Compose configuration is valid."

.PHONY: build
build:
	$(DC_FULL) build

.PHONY: up
up: up-full

.PHONY: up-core
up-core: doctor
	$(DC) up --build -d

.PHONY: up-full
up-full: doctor
	$(DC_FULL) up --build -d

.PHONY: up-observability
up-observability: doctor
	$(DC_OBS) up --build -d

.PHONY: down
down:
	$(DC_FULL) down --remove-orphans

.PHONY: restart
restart:
	$(DC_FULL) down --remove-orphans
	$(DC_FULL) up --build -d

.PHONY: ps
ps:
	$(DC_FULL) ps

.PHONY: ps-core
ps-core:
	$(DC) ps

.PHONY: logs
logs:
	$(DC_FULL) logs -f

.PHONY: api-logs
api-logs:
	$(DC_FULL) logs -f api

.PHONY: dashboard-logs
dashboard-logs:
	$(DC_FULL) logs -f dashboard

.PHONY: db-logs
db-logs:
	$(DC_FULL) logs -f postgres

.PHONY: health
health:
	@./scripts/verify-services.sh

.PHONY: health-core
health-core:
	@./scripts/verify-core-services.sh

.PHONY: api-health
api-health:
	curl -fsS http://localhost:8000/health | python -m json.tool

.PHONY: db-shell
db-shell:
	$(DC_FULL) exec postgres psql -U warehouse_user -d warehouse_ai

.PHONY: redis-shell
redis-shell:
	$(DC_FULL) exec redis redis-cli

.PHONY: api-shell
api-shell:
	$(DC_FULL) exec api /bin/sh

.PHONY: clean
clean:
	@./scripts/docker-clean.sh

.PHONY: reset
reset:
	$(DC_FULL) down -v --remove-orphans

.PHONY: prod-config
prod-config: env validate-env
	@$(DC_PROD) config >/dev/null
	@echo "Production Compose configuration is valid."

.PHONY: prod-up
prod-up: prod-config
	$(DC_PROD) up --build -d

.PHONY: prod-up-obs
prod-up-obs: prod-config
	$(DC_PROD_OBS) up --build -d

.PHONY: prod-ps
prod-ps:
	$(DC_PROD_OBS) ps

.PHONY: prod-down
prod-down:
	$(DC_PROD_OBS) down --remove-orphans

.PHONY: db-current
db-current:
	$(DC_FULL) exec api alembic current

.PHONY: db-heads
db-heads:
	$(DC_FULL) exec api alembic heads

.PHONY: db-history
db-history:
	$(DC_FULL) exec api alembic history

.PHONY: db-upgrade
db-upgrade:
	$(DC_FULL) exec api alembic upgrade head

.PHONY: db-downgrade
db-downgrade:
	$(DC_FULL) exec api alembic downgrade -1

.PHONY: db-revision
db-revision:
	@if [ -z "$(MSG)" ]; then \
		echo "Usage: make db-revision MSG=\"create initial schema\""; \
		exit 1; \
	fi
	$(DC_FULL) exec api alembic revision --autogenerate -m "$(MSG)"

.PHONY: db-check-alembic
db-check-alembic:
	$(DC_FULL) exec api python -m app.scripts.check_alembic_setup
	$(DC_FULL) exec api alembic current
	$(DC_FULL) exec api alembic heads

.PHONY: db-check-models
db-check-models:
	$(DC_FULL) exec api python -m app.scripts.check_model_metadata

.PHONY: db-check-schema
db-check-schema:
	$(DC_FULL) exec api python -m app.scripts.check_database_schema

.PHONY: db-seed
db-seed:
	$(DC_FULL) exec api python -m app.scripts.seed_database

.PHONY: db-generate-demo-data
db-generate-demo-data:
	$(DC_FULL) exec api python -m app.scripts.generate_demo_data

.PHONY: db-check-data
db-check-data:
	$(DC_FULL) exec api python -m app.scripts.check_seed_data

.PHONY: db-table-counts
db-table-counts:
	$(DC_FULL) exec api python -m app.scripts.show_table_counts

.PHONY: db-backup
db-backup:
	@./scripts/db-backup.sh

.PHONY: db-restore
db-restore:
	@if [ -z "$(BACKUP)" ]; then \
		echo "Usage: make db-restore BACKUP=backups/warehouse_ai_YYYYMMDD_HHMMSS.sql"; \
		exit 1; \
	fi
	@./scripts/db-restore.sh "$(BACKUP)"

.PHONY: db-verify
db-verify:
	$(DC_FULL) exec api python -m app.scripts.check_database_connection
	$(DC_FULL) exec api python -m app.scripts.check_model_metadata
	$(DC_FULL) exec api python -m app.scripts.check_alembic_setup
	$(DC_FULL) exec api python -m app.scripts.check_database_schema
	$(DC_FULL) exec api python -m app.scripts.check_seed_data
	$(DC_FULL) exec api python -m app.scripts.show_table_counts

.PHONY: api-openapi
api-openapi:
	curl -fsS http://localhost:8000/openapi.json >/dev/null
	@echo "OpenAPI document is available."

.PHONY: api-docs-check
api-docs-check:
	curl -fsS http://localhost:8000/docs >/dev/null
	@echo "Swagger UI is available."

.PHONY: api-routes
api-routes:
	$(DC_FULL) exec api python -m app.scripts.show_api_routes

.PHONY: api-verify-foundation
api-verify-foundation:
	curl -fsS http://localhost:8000/health >/dev/null
	curl -fsS http://localhost:8000/api/v1 >/dev/null
	curl -fsS http://localhost:8000/openapi.json >/dev/null
	$(DC_FULL) exec api python -m app.scripts.show_api_routes
	@echo "API foundation verification successful."

.PHONY: api-verify-common
api-verify-common:
	curl -fsS http://localhost:8000/health >/dev/null
	curl -fsS http://localhost:8000/api/v1 >/dev/null
	curl -fsS http://localhost:8000/openapi.json >/dev/null
	$(DC_FULL) exec api python -m app.scripts.check_api_error_foundation
	@STATUS=$$(curl -s -o /tmp/warehouse_api_404.json -w "%{http_code}" http://localhost:8000/api/v1/not-found-check); \
		test "$$STATUS" = "404"; \
		grep -q '"error"' /tmp/warehouse_api_404.json; \
		grep -q '"request_id"' /tmp/warehouse_api_404.json; \
		echo "Standard 404 error response verified."
	$(DC_FULL) exec api python -m app.scripts.show_api_routes
	@echo "Common API foundation verification successful."

.PHONY: api-verify-runs-agents
api-verify-runs-agents:
	curl -fsS http://localhost:8000/health >/dev/null
	curl -fsS http://localhost:8000/api/v1/runs >/dev/null
	curl -fsS http://localhost:8000/api/v1/agents >/dev/null
	curl -fsS http://localhost:8000/openapi.json >/dev/null
	$(DC_FULL) exec api python -m app.scripts.check_runs_agents_api_foundation
	@echo "Runs and agents API verification successful."

.PHONY: api-verify-events
api-verify-events:
	curl -fsS http://localhost:8000/health >/dev/null
	curl -fsS http://localhost:8000/api/v1/events >/dev/null
	curl -fsS http://localhost:8000/openapi.json >/dev/null
	$(DC_FULL) exec api python -m app.scripts.check_events_api_foundation
	@echo "Events API verification successful."

.PHONY: api-verify-metrics
api-verify-metrics:
	curl -fsS http://localhost:8000/health >/dev/null
	curl -fsS http://localhost:8000/api/v1/metrics >/dev/null
	curl -fsS http://localhost:8000/openapi.json >/dev/null
	$(DC_FULL) exec api python -m app.scripts.check_metrics_api_foundation
	@echo "Metrics API verification successful."

.PHONY: api-verify-websockets
api-verify-websockets:
	$(DC_FULL) exec api python -m app.scripts.check_websocket_streams
	@echo "WebSocket stream verification successful."

.PHONY: api-verify-metrics-streams
api-verify-metrics-streams:
	$(MAKE) api-verify-metrics
	$(MAKE) api-verify-websockets
	@echo "Metrics and WebSocket stream verification successful."

.PHONY: api-verify-training
api-verify-training:
	curl -fsS http://localhost:8000/health >/dev/null
	curl -fsS http://localhost:8000/api/v1/training >/dev/null
	curl -fsS http://localhost:8000/openapi.json >/dev/null
	$(DC_FULL) exec api python -m app.scripts.check_training_api_foundation
	@echo "Training API verification successful."

.PHONY: api-verify-checkpoints-models
api-verify-checkpoints-models:
	curl -fsS http://localhost:8000/health >/dev/null
	curl -fsS http://localhost:8000/api/v1/checkpoints >/dev/null
	curl -fsS http://localhost:8000/api/v1/models >/dev/null
	curl -fsS http://localhost:8000/openapi.json >/dev/null
	$(DC_FULL) exec api python -m app.scripts.check_checkpoints_models_api_foundation
	@echo "Checkpoints and model registry API verification successful."

