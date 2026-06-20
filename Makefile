SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Warehouse AI Simulator - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make env              Create .env from .env.example if missing"
	@echo "  make validate-env     Validate required environment variables"
	@echo "  make doctor           Validate Docker, env, and compose config"
	@echo ""
	@echo "Docker:"
	@echo "  make build            Build all Docker images"
	@echo "  make up               Start all services"
	@echo "  make down             Stop all services"
	@echo "  make restart          Restart all services"
	@echo "  make ps               Show service status"
	@echo "  make logs             Follow all logs"
	@echo "  make clean            Stop services and prune dangling resources"
	@echo "  make reset            Stop services and remove volumes"
	@echo ""
	@echo "Health:"
	@echo "  make health           Verify all service health endpoints"
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
	@docker compose config >/dev/null
	@echo "Docker Compose configuration is valid."

.PHONY: build
build:
	docker compose build

.PHONY: up
up: doctor
	docker compose up --build -d

.PHONY: down
down:
	docker compose down

.PHONY: restart
restart:
	docker compose down
	docker compose up --build -d

.PHONY: ps
ps:
	docker compose ps

.PHONY: logs
logs:
	docker compose logs -f

.PHONY: api-logs
api-logs:
	docker compose logs -f api

.PHONY: dashboard-logs
dashboard-logs:
	docker compose logs -f dashboard

.PHONY: db-logs
db-logs:
	docker compose logs -f postgres

.PHONY: health
health:
	@./scripts/verify-services.sh

.PHONY: api-health
api-health:
	curl -fsS http://localhost:8000/health | python -m json.tool

.PHONY: db-shell
db-shell:
	docker compose exec postgres psql -U warehouse_user -d warehouse_ai

.PHONY: redis-shell
redis-shell:
	docker compose exec redis redis-cli

.PHONY: api-shell
api-shell:
	docker compose exec api /bin/sh

.PHONY: clean
clean:
	@./scripts/docker-clean.sh

.PHONY: reset
reset:
	docker compose down -v
