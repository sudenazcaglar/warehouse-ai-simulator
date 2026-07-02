# Phase 4C Runs and Agents API Evidence

## Goal

Phase 4C adds the first database-backed REST API endpoints for simulation runs and agents.

## Added

- Run create schema
- Run response schema
- Run paginated list schema
- Agent response schema
- Agent paginated list schema
- Runs repository
- Agents repository
- Database-backed runs router
- Database-backed agents router
- Run agents endpoint
- Runs and agents API verification script
- Runs and agents API verification Makefile command
- API documentation updates

## Added Endpoints

```text
POST /api/v1/runs
GET  /api/v1/runs
GET  /api/v1/runs/{run_id}
GET  /api/v1/runs/{run_id}/agents

GET  /api/v1/agents
GET  /api/v1/agents/{agent_id}

GET  /api/v1/runs/status
GET  /api/v1/agents/status
```

The existing module status endpoints remain available.

## Supported Features

- UUID-based lookup
- Invalid UUID error handling
- Missing resource (`404`) handling
- Pagination
- Status filtering
- Name search
- Environment search
- Policy search
- Sorting
- OpenAPI schema visibility

## Verification Commands

```bash
curl http://localhost:8000/api/v1/runs
curl http://localhost:8000/api/v1/agents
curl -i http://localhost:8000/api/v1/runs/not-a-valid-id
make api-verify-common
make api-verify-runs-agents
docker compose logs api --tail=100
```

## Expected Result

```text
Runs and agents API verification successful.
```

## Verification Result

The following commands were executed successfully:

```bash
curl http://localhost:8000/api/v1/runs
curl http://localhost:8000/api/v1/agents
curl -i http://localhost:8000/api/v1/runs/not-a-valid-id
curl -i http://localhost:8000/api/v1/agents/not-a-valid-id
make api-verify-common
make api-verify-runs-agents
```

### Runs List Result

`GET /api/v1/runs` returned a paginated response containing simulation run records.

The following response fields were verified:

- `items`
- `total`
- `page`
- `page_size`
- `pages`
- `has_next`
- `has_previous`

### Agents List Result

`GET /api/v1/agents` returned a paginated response containing agent records.

The following response fields were verified:

- `items`
- `total`
- `page`
- `page_size`
- `pages`
- `has_next`
- `has_previous`

### Invalid UUID Verification

Invalid run ID request returned:

```http
HTTP/1.1 400 Bad Request
```

Response body:

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

Invalid agent ID request returned:

```http
HTTP/1.1 400 Bad Request
```

Response body:

```json
{
  "error": {
    "code": "invalid_uuid",
    "message": "Invalid UUID value for 'agent_id'.",
    "details": {
      "field": "agent_id",
      "value": "not-a-valid-id"
    },
    "request_id": "request-id"
  }
}
```

### Common API Verification Result

```text
Common API error foundation verification successful.
Standard 404 error response verified.
Common API foundation verification successful.
```

### Runs and Agents API Verification Result

```text
Runs and agents API verification successful.

Verified endpoints:
- GET /api/v1/runs
- POST /api/v1/runs
- GET /api/v1/runs/{run_id}
- GET /api/v1/runs/{run_id}/agents
- GET /api/v1/agents

Verified features:
- Invalid UUID handling
- Missing resource (404) handling
- Pagination response format
- OpenAPI availability
```

### Route Verification Result

The following routes were successfully registered:

```text
GET  /api/v1/agents
GET  /api/v1/agents/{agent_id}
POST /api/v1/runs
GET  /api/v1/runs
GET  /api/v1/runs/{run_id}
GET  /api/v1/runs/{run_id}/agents
```

## Result

Phase 4C completed successfully. The backend now provides database-backed simulation run and agent APIs with pagination, filtering, sorting, UUID validation, standardized error handling, OpenAPI documentation, and automated verification support.
