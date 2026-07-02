# Phase 4D Event Ingestion and Agent Timeline API Evidence

## Goal

Phase 4D adds event ingestion and event query APIs for robot telemetry and simulation events.

## Added

- Event create schema
- Event response schema
- Event paginated list schema
- Events repository
- Database-backed events router
- Agent timeline endpoint
- Run events endpoint
- Event relationship validation
- Event API verification script
- Event API verification Makefile command
- API documentation updates

## Added Endpoints

```text
POST /api/v1/events
GET  /api/v1/events
GET  /api/v1/agents/{agent_id}/timeline
GET  /api/v1/runs/{run_id}/events

GET  /api/v1/events/status
```

The existing module status endpoint remains available.

## Supported Features

- Single event ingestion
- Optional episode relationship
- Event type enum validation
- Simulation run filtering
- Agent filtering
- Episode filtering
- Event type filtering
- Reason code filtering
- Time range filtering
- Pagination
- Ascending timeline ordering
- Run-agent relationship validation
- Episode-run relationship validation
- Invalid UUID handling
- Missing resource handling
- Relationship mismatch (`409 Conflict`) handling
- OpenAPI schema visibility

## Verification Commands

```bash
curl -X POST http://localhost:8000/api/v1/events
curl http://localhost:8000/api/v1/events
curl http://localhost:8000/api/v1/agents/{agent_id}/timeline
curl http://localhost:8000/api/v1/runs/{run_id}/events
make api-verify-common
make api-verify-runs-agents
make api-verify-events
docker compose logs api --tail=100
```

## Expected Result

```text
Events API verification successful.
```

## Verification Result

The following commands were executed successfully:

```bash
curl http://localhost:8000/api/v1/events
curl -i "http://localhost:8000/api/v1/events?simulation_run_id=not-a-valid-id"
make api-verify-common
make api-verify-runs-agents
make api-verify-events
```

### Events List Result

`GET /api/v1/events` returned a paginated response containing event records.

The following response fields were verified:

- `items`
- `total`
- `page`
- `page_size`
- `pages`
- `has_next`
- `has_previous`

### Invalid UUID Verification

An invalid simulation run ID filter returned:

```http
HTTP/1.1 400 Bad Request
```

Response body:

```json
{
  "error": {
    "code": "invalid_uuid",
    "message": "Invalid UUID value for 'simulation_run_id'.",
    "details": {
      "field": "simulation_run_id",
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

### Runs and Agents Regression Verification Result

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

### Events API Verification Result

```text
Events API verification successful.

Verified endpoints:
- POST /api/v1/events
- GET /api/v1/events
- GET /api/v1/events?event_type=moved
- GET /api/v1/agents/{agent_id}/timeline
- GET /api/v1/runs/{run_id}/events

Verified features:
- Invalid UUID handling
- Missing resource (404) handling
- Run-agent relationship validation
- Pagination response format
- Timeline ascending ordering
- OpenAPI availability
```

### Route Verification Result

The following routes were successfully registered:

```text
POST /api/v1/events
GET  /api/v1/events
GET  /api/v1/events/status
GET  /api/v1/agents/{agent_id}/timeline
GET  /api/v1/runs/{run_id}/events
```

## Result

Phase 4D completed successfully. The backend now supports event ingestion, event listing, agent timeline queries, simulation run event queries, event filtering, pagination, UUID validation, standardized error handling, relationship validation, OpenAPI documentation, and automated API verification.
