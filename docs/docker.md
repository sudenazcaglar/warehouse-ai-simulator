# Docker Development Environment

This document describes the Docker-based development environment for the Warehouse AI Simulator project.

## Goal

The goal of the Docker setup is to provide a reproducible local development environment for the core system services.

## Services

| Service     | Container Name        |        Port | Purpose                            |
| ----------- | --------------------- | ----------: | ---------------------------------- |
| API         | warehouse-api         |        8000 | FastAPI backend                    |
| Dashboard   | warehouse-dashboard   |        3000 | React / Vite dashboard             |
| PostgreSQL  | warehouse-postgres    |        5432 | Relational database                |
| Redis       | warehouse-redis       |        6379 | Cache and lightweight coordination |
| MinIO       | warehouse-minio       | 9000 / 9001 | Object storage and console         |
| Prometheus  | warehouse-prometheus  |        9090 | Metrics collection                 |
| Grafana     | warehouse-grafana     |        3001 | Monitoring dashboards              |
| TensorBoard | warehouse-tensorboard |        6006 | Training visualization             |
| Nginx       | warehouse-nginx       |        8080 | Reverse proxy gateway              |

## Recommended Workflow

Create `.env` if it does not exist:

```bash
make env
```

Validate environment variables:

```bash
make validate-env
```

Run a full local diagnostic:

```bash
make doctor
```

Start all services:

```bash
make up
```

Check status:

```bash
make ps
```

Verify all services:

```bash
make health
```

Stop all services:

```bash
make down
```

## Manual Docker Commands

Start the environment:

```bash
docker compose up --build -d
```

Check service status:

```bash
docker compose ps
```

Stop the environment:

```bash
docker compose down
```

Stop and remove volumes:

```bash
docker compose down -v
```

## Health Checks

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
curl http://localhost:3000
curl http://localhost:8080/api/health
curl http://localhost:9000/minio/health/live
curl http://localhost:9090/-/healthy
curl http://localhost:3001/api/health
curl http://localhost:6006
```

## PostgreSQL Check

```bash
docker compose exec postgres pg_isready -U warehouse_user -d warehouse_ai
```

## Redis Check

```bash
docker compose exec redis redis-cli ping
```

## Browser URLs

| Service       | URL                          |
| ------------- | ---------------------------- |
| Dashboard     | <http://localhost:3000>      |
| API Docs      | <http://localhost:8000/docs> |
| Nginx Gateway | <http://localhost:8080>      |
| MinIO Console | <http://localhost:9001>      |
| Prometheus    | <http://localhost:9090>      |
| Grafana       | <http://localhost:3001>      |
| TensorBoard   | <http://localhost:6006>      |

## Default Credentials

### Grafana

```text
username: admin
password: admin
```

### MinIO

```text
username: minioadmin
password: minioadmin
```

## Local Machine Notes

The local Docker environment is intended for development and integration testing. Heavy reinforcement learning training will be performed on cloud GPU instances in later phases.

## Phase 2B Result

The Docker environment now includes a repeatable developer workflow with Makefile commands, environment validation, automated health checks, and documented operational procedures.

## Compose Profiles

The development Compose file supports profiles to reduce local resource usage.

### Core Development Environment

Starts only the essential services:

```bash
make up-core
make health-core
```

Core services:

- API
- Dashboard
- PostgreSQL
- Redis
- MinIO
- Nginx

### Full Development Environment

Starts all development services:

```bash
make up-full
make health
```

Full services include:

- Core services
- Prometheus
- Grafana
- TensorBoard

### Observability Profile

Starts core services with Prometheus and Grafana:

```bash
make up-observability
```

### Production-Like Environment

The project includes a separate production-like Compose file:

```bash
make prod-config
make prod-up
make prod-ps
```

Production-like differences:

- API runs without auto-reload
- Dashboard is built as static assets
- Dashboard is served by Nginx
- Database and Redis are not exposed to the host
- Public access goes through the Nginx gateway
- Observability can be enabled with a profile

Start production-like environment with observability:

```bash
make prod-up-obs
```

Stop production-like environment:

```bash
make prod-down
```
