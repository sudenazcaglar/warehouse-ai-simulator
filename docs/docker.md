# Docker Development Environment

This document describes the Docker-based development environment for the Warehouse AI Simulator project.

## Goal

The goal of the Docker setup is to provide a reproducible local development environment for the core system services.

## Services

| Service | Container Name | Port | Purpose |
|---|---:|---:|---|
| API | warehouse-api | 8000 | FastAPI backend |
| Dashboard | warehouse-dashboard | 3000 | React / Vite dashboard |
| PostgreSQL | warehouse-postgres | 5432 | Relational database |
| Redis | warehouse-redis | 6379 | Cache and lightweight coordination |
| MinIO | warehouse-minio | 9000 / 9001 | Object storage and console |
| Prometheus | warehouse-prometheus | 9090 | Metrics collection |
| Grafana | warehouse-grafana | 3001 | Monitoring dashboards |
| TensorBoard | warehouse-tensorboard | 6006 | Training visualization |
| Nginx | warehouse-nginx | 8080 | Reverse proxy gateway |

## Start the Environment

```bash
docker compose up --build -d
```

## Check Service Status

```bash
docker compose ps
```

## Stop the Environment

```bash
docker compose down
```

## Stop and Remove Volumes

Use this only when you want to delete local database, Redis, MinIO, Prometheus, and Grafana data.

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

| Service | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |
| Nginx Gateway | http://localhost:8080 |
| MinIO Console | http://localhost:9001 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 |
| TensorBoard | http://localhost:6006 |

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

## Phase 2A Result

The initial Dockerized development foundation successfully runs the core local services required for backend development, dashboard development, database integration, object storage, metrics collection, monitoring, and training visualization.
