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

---

# Common API Standards

Phase 4B defines shared API standards for response schemas, errors, pagination, dependencies, and logging.

## Standard Error Response

Errors use the following response format:

```json
{
  "error": {
    "code": "not_found",
    "message": "Resource not found.",
    "details": {},
    "request_id": "request-id"
  }
}
```

## Error Types

The API defines common error classes for:

- Bad request
- Not found
- Conflict
- Database operation failure
- Validation failure
- Unhandled internal errors

## Pagination

The API supports the following pagination parameters:

- `page`
- `page_size`
- `offset`
- `limit`

### Default Values

```text
page=1
page_size=20
```

### Maximum Page Size

```text
100
```

## Request ID

Each request is assigned a unique request identifier.

The request ID is returned in the following response header:

```text
X-Request-ID
```

It is also included in standard error responses.

## Request Logging

The API logs the following request lifecycle events:

- `request_started`
- `request_completed`
- `request_failed`

Each log entry includes:

- Request ID
- HTTP method
- Request path
- HTTP status code
- Request duration (milliseconds)

## Database Dependency

The shared database dependency is responsible for:

- Session creation
- Rollback on exceptions
- Database error logging
- Session cleanup

## UUID Validation

A shared UUID validation helper is available for validating endpoint path and query parameters.

---

# Runs and Agents API

Phase 4C adds the first database-backed REST API endpoints.

## Runs

### Create Run

```http
POST /api/v1/runs
```

Example request:

```json
{
  "run_name": "api-created-run",
  "environment_name": "WarehouseSimulator-API",
  "agent_count": 3,
  "map_version": "2026.api",
  "status": "created",
  "config_json": {
    "source": "api"
  }
}
```

### List Runs

```http
GET /api/v1/runs
```

Supported query parameters:

- `page`
- `page_size`
- `status`
- `run_name`
- `environment_name`
- `sort_by`
- `sort_order`

Supported sort fields:

- `created_at`
- `started_at`
- `run_name`
- `status`

### Get Run Detail

```http
GET /api/v1/runs/{run_id}
```

### Get Agents for a Run

```http
GET /api/v1/runs/{run_id}/agents
```

---

## Agents

### List Agents

```http
GET /api/v1/agents
```

Supported query parameters:

- `page`
- `page_size`
- `status`
- `simulation_run_id`
- `agent_name`
- `policy_name`
- `sort_by`
- `sort_order`

Supported sort fields:

- `created_at`
- `agent_name`
- `status`

### Get Agent Detail

```http
GET /api/v1/agents/{agent_id}
```

---

## Error Behavior

### Invalid UUID

Invalid UUID values return:

```json
{
  "error": {
    "code": "invalid_uuid",
    "message": "Invalid UUID value for 'run_id'.",
    "details": {
      "field": "run_id",
      "value": "not-a-valid-id"
    },
    "request_id": "request-id"
  }
}
```

### Resource Not Found

Missing resources return:

```json
{
  "error": {
    "code": "not_found",
    "message": "Simulation run not found.",
    "details": {
      "run_id": "uuid"
    },
    "request_id": "request-id"
  }
}
```

---

# Events API

Phase 4D adds event ingestion and event timeline APIs.

## Create Event

```http
POST /api/v1/events
```

Example request:

```json
{
  "simulation_run_id": "run-uuid",
  "episode_id": null,
  "agent_id": "agent-uuid",
  "step": 1250,
  "position_x": 4.2,
  "position_z": 8.1,
  "velocity": 1.4,
  "action": "move_to_target",
  "reward_delta": 0.05,
  "event_type": "moved",
  "reason_code": "normal_operation",
  "metadata_json": {
    "source": "api"
  }
}
```

The API validates:

- Simulation run existence
- Agent existence
- Agent belongs to the specified simulation run
- Optional episode existence
- Optional episode belongs to the specified simulation run

## List Events

```http
GET /api/v1/events
```

Supported query parameters:

- `page`
- `page_size`
- `simulation_run_id`
- `agent_id`
- `episode_id`
- `event_type`
- `reason_code`
- `start_time`
- `end_time`
- `sort_order`

Default sorting:

```text
timestamp desc
```

## Agent Timeline

```http
GET /api/v1/agents/{agent_id}/timeline
```

This endpoint returns the event timeline for a single agent.

Default sorting:

```text
timestamp asc
```

## Run Events

```http
GET /api/v1/runs/{run_id}/events
```

This endpoint returns all events associated with a single simulation run.

## Error Behavior

### Invalid UUID

Invalid UUID values return a **400 Bad Request** with the `invalid_uuid` error code.

### Missing Resources

Missing simulation runs, agents, or episodes return a **404 Not Found** with the `not_found` error code.

### Relationship Mismatch

Relationship validation failures return a **409 Conflict** response.

Example:

```json
{
  "error": {
    "code": "agent_run_mismatch",
    "message": "Agent does not belong to the provided simulation run.",
    "details": {},
    "request_id": "request-id"
  }
}
```

---

# Metrics API and WebSocket Streams

Phase 4E adds metrics ingestion, metrics query endpoints, and live WebSocket streams.

## Metrics

### Create Metric

```http
POST /api/v1/metrics
```

Example request:

```json
{
  "simulation_run_id": "run-uuid",
  "training_session_id": "training-session-uuid",
  "metric_name": "episode_reward",
  "metric_value": 12.5,
  "metric_unit": "score",
  "source": "training",
  "metadata_json": {
    "episode": 12
  }
}
```

### List Metrics

```http
GET /api/v1/metrics
```

Supported query parameters:

- `page`
- `page_size`
- `simulation_run_id`
- `training_session_id`
- `metric_name`
- `source`
- `start_time`
- `end_time`
- `sort_order`

### Run Metrics

```http
GET /api/v1/runs/{run_id}/metrics
```

### Training Metrics

```http
GET /api/v1/training/{training_id}/metrics
```

---

# WebSocket Streams

## Run Metrics Stream

```text
ws://localhost:8000/ws/runs/{run_id}/metrics
```

This endpoint broadcasts metrics posted for the specified simulation run.

Example payload:

```json
{
  "type": "metric",
  "data": {
    "id": "metric-uuid",
    "simulation_run_id": "run-uuid",
    "training_session_id": "training-session-uuid",
    "metric_name": "episode_reward",
    "metric_value": 12.5,
    "metric_unit": "score",
    "source": "training",
    "timestamp": "2026-07-02T10:00:00Z",
    "metadata_json": {}
  }
}
```

## Agent Events Stream

```text
ws://localhost:8000/ws/agents/{agent_id}/events
```

This endpoint broadcasts events posted for the specified agent.

Example payload:

```json
{
  "type": "agent_event",
  "data": {
    "id": "event-uuid",
    "agent_id": "agent-uuid",
    "simulation_run_id": "run-uuid",
    "event_type": "custom",
    "action": "move_to_target"
  }
}
```

## WebSocket Scope

The initial WebSocket implementation uses an in-memory connection manager.

It is designed for local development and API verification. A distributed pub/sub backend can be introduced later to support deployments with multiple API replicas.

---

# Training API

Phase 4F adds database-backed training session APIs.

This phase does **not** start a real ML-Agents process. Instead, the `training/start` endpoint creates a `TrainingSession` record in the database and marks it as running.

## Start Training

```http
POST /api/v1/training/start
```

Example request:

```json
{
  "simulation_run_id": "run-uuid",
  "environment_config_id": null,
  "algorithm": "ppo",
  "max_steps": 100000,
  "learning_rate": 0.0003,
  "batch_size": 64,
  "buffer_size": 2048,
  "checkpoint_interval": 5000
}
```

The created training session starts with:

```text
status=running
current_step=0
```

## Stop Training

```http
POST /api/v1/training/{training_id}/stop
```

Example request:

```json
{
  "status": "completed"
}
```

Supported stop statuses:

- `completed`
- `cancelled`
- `failed`

Stopping a training session sets the `ended_at` timestamp.

Repeated stop attempts on a terminal training session return a **409 Conflict** response.

## List Training Sessions

```http
GET /api/v1/training
```

Supported query parameters:

- `page`
- `page_size`
- `simulation_run_id`
- `status`
- `algorithm`
- `sort_by`
- `sort_order`

Supported sort fields:

- `created_at`
- `started_at`
- `updated_at`
- `status`
- `algorithm`

## Get Training Detail

```http
GET /api/v1/training/{training_id}
```

## Training Metrics

```http
GET /api/v1/training/{training_id}/metrics
```

This endpoint was introduced in **Phase 4E** and remains available in **Phase 4F**.

## Error Behavior

### Invalid UUID

Invalid UUID values return a **400 Bad Request** with the `invalid_uuid` error code.

### Missing Resources

Missing training sessions or simulation runs return a **404 Not Found** with the `not_found` error code.

### Training Already Stopped

Repeated stop attempts return a **409 Conflict** response.

Example:

```json
{
  "error": {
    "code": "training_already_stopped",
    "message": "Training session is already in a terminal state.",
    "details": {},
    "request_id": "request-id"
  }
}
```

---

# Checkpoints and Model Registry API

Phase 4G adds checkpoint metadata and model registry metadata APIs.

## Checkpoints

### Create Checkpoint

```http
POST /api/v1/checkpoints
```

Example request:

```json
{
  "training_session_id": "training-session-uuid",
  "step": 50000,
  "reward_mean": 42.5,
  "success_rate": 0.91,
  "collision_rate": 0.03,
  "file_path": "s3://warehouse-ai/checkpoints/run-1/step-50000.pt",
  "storage_backend": "minio",
  "is_best": true,
  "metadata_json": {
    "source": "api"
  }
}
```

If `is_best=true`, any existing best checkpoints for the same training session are automatically unset.

### List Checkpoints

```http
GET /api/v1/checkpoints
```

Supported query parameters:

- `page`
- `page_size`
- `training_session_id`
- `is_best`
- `sort_by`
- `sort_order`

Supported sort fields:

- `created_at`
- `step`
- `reward_mean`
- `success_rate`
- `collision_rate`

### Get Checkpoint Detail

```http
GET /api/v1/checkpoints/{checkpoint_id}
```

### Get Best Checkpoint

```http
GET /api/v1/checkpoints/best
```

Optional query parameter:

- `training_session_id`

---

## Model Registry

### Create Model Version

```http
POST /api/v1/models
```

Example request:

```json
{
  "training_session_id": "training-session-uuid",
  "checkpoint_id": "checkpoint-uuid",
  "model_name": "ppo-warehouse-policy",
  "version": "v1.0.0",
  "algorithm": "ppo",
  "file_path": "s3://warehouse-ai/models/ppo-warehouse-policy/v1.0.0/model.pt",
  "onnx_path": "s3://warehouse-ai/models/ppo-warehouse-policy/v1.0.0/model.onnx",
  "reward_mean": 42.5,
  "success_rate": 0.91,
  "collision_rate": 0.03,
  "is_active": true,
  "metadata_json": {
    "source": "api"
  }
}
```

The API enforces uniqueness for:

```text
model_name + version
```

If `is_active=true`, any existing active model with the same `model_name` is automatically deactivated.

### List Model Versions

```http
GET /api/v1/models
```

Supported query parameters:

- `page`
- `page_size`
- `training_session_id`
- `checkpoint_id`
- `model_name`
- `version`
- `is_active`
- `sort_by`
- `sort_order`

### Get Model Version Detail

```http
GET /api/v1/models/{model_id}
```

### Active Models

```http
GET /api/v1/models/active
```

Optional query parameter:

- `model_name`

This endpoint returns a paginated list of active model versions.

---

## Error Behavior

### Duplicate Checkpoint Step

```json
{
  "error": {
    "code": "checkpoint_step_exists",
    "message": "Checkpoint already exists for this training session and step.",
    "details": {},
    "request_id": "request-id"
  }
}
```

### Duplicate Model Version

```json
{
  "error": {
    "code": "model_version_exists",
    "message": "Model version already exists.",
    "details": {},
    "request_id": "request-id"
  }
}
```

### Invalid UUID

Invalid UUID values return a **400 Bad Request** with the `invalid_uuid` error code.

### Missing Resources

Missing training sessions, checkpoints, or model versions return a **404 Not Found** with the `not_found` error code.

### Relationship Mismatch

Relationship validation failures return a **409 Conflict** response.
