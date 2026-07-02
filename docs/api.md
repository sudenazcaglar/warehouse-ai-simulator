# API Documentation

The backend API is implemented with FastAPI.

## Base URLs

### Local Development

```text
http://localhost:8000
```

### Swagger UI

```text
http://localhost:8000/docs
```

### OpenAPI JSON

```text
http://localhost:8000/openapi.json
```

## API Namespace

The current API namespace is:

```text
/api/v1
```

## REST Modules

Phase 4 defines the following backend API modules:

| Module       | Path                   | Purpose                       |
| ------------ | ---------------------- | ----------------------------- |
| Health       | `/health`              | API and database health       |
| Runs         | `/api/v1/runs`         | Simulation run management     |
| Training     | `/api/v1/training`     | Training session management   |
| Agents       | `/api/v1/agents`       | Agent records and timelines   |
| Events       | `/api/v1/events`       | Event ingestion and querying  |
| Metrics      | `/api/v1/metrics`      | Metric ingestion and querying |
| Checkpoints  | `/api/v1/checkpoints`  | Checkpoint metadata           |
| Models       | `/api/v1/models`       | Model registry metadata       |
| Explanations | `/api/v1/explanations` | LLM explanation records       |
| Stream       | `/api/v1/stream`       | Stream module metadata        |

## WebSocket Scope

The following WebSocket endpoints are planned:

```text
/ws/runs/{run_id}/metrics
/ws/agents/{agent_id}/events
```

WebSocket support will be implemented in **Phase 4E**.

## Phase 4A Status

Phase 4A establishes the modular API architecture and route registration layer.

The resource modules currently expose module status endpoints under:

```text
/ api/v1/{module}/status
```

Database-backed CRUD endpoints will be implemented in the subsequent Phase 4 subphases.
