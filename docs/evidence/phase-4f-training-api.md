# Phase 4F Training API Evidence

## Goal

Phase 4F adds database-backed training session APIs for starting, stopping, listing, and reading training sessions.

This phase does **not** start a real ML-Agents process. Instead, it creates and manages `TrainingSession` records through the API.

## Added

- Training start schema
- Training stop schema
- Training response schema
- Training paginated list schema
- Training repository
- Training start endpoint
- Training stop endpoint
- Training list endpoint
- Training detail endpoint
- Training metrics endpoint preservation
- Training status transition handling
- Training API verification script
- Training API verification Makefile command
- API documentation updates

## Added Endpoints

```text
POST /api/v1/training/start
POST /api/v1/training/{training_id}/stop
GET  /api/v1/training
GET  /api/v1/training/{training_id}
GET  /api/v1/training/{training_id}/metrics

GET  /api/v1/training/status
```

The existing module status endpoint remains available.

## Supported Features

- Training session creation
- Training session termination
- Terminal status handling
- Repeated stop conflict handling
- Training detail lookup
- Training list pagination
- Status filtering
- Algorithm filtering
- Simulation run filtering
- Sorting
- Invalid UUID handling
- Missing resource handling
- OpenAPI schema visibility

## Verification Commands

```bash
curl http://localhost:8000/api/v1/training
curl -i http://localhost:8000/api/v1/training/not-a-valid-id
make api-verify-common
make api-verify-runs-agents
make api-verify-events
make api-verify-metrics-streams
make api-verify-training
docker compose logs api --tail=150
```

## Expected Result

```text
Training API verification successful.
```

## Verification Result

The following commands were executed successfully:

```bash
curl http://localhost:8000/api/v1/training
curl -i http://localhost:8000/api/v1/training/not-a-valid-id
make api-verify-training
```

### Training List Result

`GET /api/v1/training` returned a paginated response containing training session records.

The following response fields were verified:

- `items`
- `total`
- `page`
- `page_size`
- `pages`
- `has_next`
- `has_previous`

### Invalid UUID Verification

An invalid training ID request returned:

```http
HTTP/1.1 400 Bad Request
```

Response body:

```json
{
  "error": {
    "code": "invalid_uuid",
    "message": "Invalid UUID value for 'training_id'.",
    "details": {
      "field": "training_id",
      "value": "not-a-valid-id"
    },
    "request_id": "request-id"
  }
}
```

### Training API Verification Result

```text
Training API verification successful.

Verified endpoints:
- POST /api/v1/training/start
- POST /api/v1/training/{training_id}/stop
- GET /api/v1/training
- GET /api/v1/training/{training_id}
- GET /api/v1/training/{training_id}/metrics

Verified features:
- Invalid UUID handling
- Missing resource (404) handling
- Repeated stop conflict handling
- Pagination response format
- OpenAPI availability
```

## Result

Phase 4F completed successfully. The backend now supports database-backed training session creation, termination, listing, detail retrieval, metrics access, training status transitions, repeated stop conflict handling, pagination, UUID validation, standardized error handling, and OpenAPI documentation.
