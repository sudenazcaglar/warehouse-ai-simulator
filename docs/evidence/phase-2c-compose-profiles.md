# Phase 2C Compose Profiles and Dev/Prod Separation Evidence

## Goal

Phase 2C introduces Docker Compose profiles and separates development and production-like environments.

## Added Capabilities

- Core development profile through default Compose services
- Full development environment with observability and training profiles
- Production-like Compose file
- Production API Dockerfile without reload
- Production dashboard Dockerfile with static build
- Production Nginx gateway configuration
- Core health verification script
- Makefile commands for dev/prod workflows

## Development Commands

```bash
make up-core
make health-core
make up-full
make health
```

## Production-Like Commands

```bash
make prod-config
make prod-up
make prod-ps
make prod-down
```

## Expected Result

The project can now run in lightweight development mode, full development mode, and production-like mode.

## Verification Result

The following workflows were verified successfully:

```bash
make up-core
make health-core

make up-full
make health

make prod-config
make prod-up
make prod-ps

curl http://localhost:8080/api/health
curl -I http://localhost:8080
```

## Observed Results

### Core Development Environment

All core services are healthy.

### Full Development Environment

All services are healthy.

### Production-Like Environment

Production Compose configuration is valid.

```text
warehouse-api-prod         Up (healthy)
warehouse-dashboard-prod   Up (healthy)
warehouse-postgres-prod    Up (healthy)
warehouse-redis-prod       Up (healthy)
warehouse-minio-prod       Up (healthy)
warehouse-nginx-prod       Up (healthy)
```

### API Gateway Response

```json
{
  "status": "healthy",
  "service": "api",
  "project": "warehouse-ai-simulator",
  "environment": "development"
}
```

### Dashboard Gateway Response

```http
HTTP/1.1 200 OK
Content-Type: text/html
```

## Result

Phase 2C completed successfully. The project now supports lightweight development mode, full development mode, and production-like Docker deployment.
