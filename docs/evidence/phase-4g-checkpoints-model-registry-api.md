# Phase 4G Checkpoints and Model Registry API Evidence

## Goal

Phase 4G adds database-backed APIs for training checkpoint metadata and model version registry metadata.

## Added

- Checkpoint create schema
- Checkpoint response schema
- Checkpoint paginated list schema
- Model version create schema
- Model version response schema
- Model version paginated list schema
- Checkpoints repository
- Model registry repository
- Checkpoint create endpoint
- Checkpoint list endpoint
- Checkpoint detail endpoint
- Best checkpoint endpoint
- Model version create endpoint
- Model version list endpoint
- Model version detail endpoint
- Active models endpoint
- Checkpoint uniqueness handling
- Model version uniqueness handling
- Active model switching
- Checkpoints and model registry verification script
- Checkpoints and model registry Makefile command
- API documentation updates

## Added Checkpoint Endpoints

```text
POST /api/v1/checkpoints
GET  /api/v1/checkpoints
GET  /api/v1/checkpoints/best
GET  /api/v1/checkpoints/{checkpoint_id}

GET  /api/v1/checkpoints/status
```

The existing module status endpoint remains available.

## Added Model Registry Endpoints

```text
POST /api/v1/models
GET  /api/v1/models
GET  /api/v1/models/active
GET  /api/v1/models/{model_id}

GET  /api/v1/models/status
```

The existing module status endpoint remains available.

## Supported Features

- Checkpoint creation
- Checkpoint listing
- Checkpoint detail lookup
- Best checkpoint lookup
- Checkpoint step uniqueness handling
- Checkpoint metric metadata
- Checkpoint artifact path metadata
- Model version creation
- Model version listing
- Model version detail lookup
- Active model listing
- Model version uniqueness handling
- Active model switching
- Model artifact path metadata
- ONNX artifact path metadata
- Training session validation
- Checkpoint-training relationship validation
- Invalid UUID handling
- Missing resource handling
- Conflict handling
- Pagination
- Sorting
- OpenAPI schema visibility

## Verification Commands

```bash
curl http://localhost:8000/api/v1/checkpoints
curl http://localhost:8000/api/v1/models
curl -i http://localhost:8000/api/v1/checkpoints/not-a-valid-id
curl -i http://localhost:8000/api/v1/models/not-a-valid-id
make api-verify-common
make api-verify-runs-agents
make api-verify-events
make api-verify-metrics-streams
make api-verify-training
make api-verify-checkpoints-models
docker compose logs api --tail=150
```

## Expected Result

```text
Checkpoints and model registry API verification successful.
```

## Verification Result

The following commands were executed successfully:

```bash
curl http://localhost:8000/api/v1/checkpoints
curl http://localhost:8000/api/v1/models
curl -i http://localhost:8000/api/v1/checkpoints/not-a-valid-id
curl -i http://localhost:8000/api/v1/models/not-a-valid-id
make api-verify-checkpoints-models
```

### Checkpoints List Result

`GET /api/v1/checkpoints` returned a paginated response containing checkpoint records.

The following pagination fields were verified:

- `items`
- `total`
- `page`
- `page_size`
- `pages`
- `has_next`
- `has_previous`

The following checkpoint response fields were verified:

- `id`
- `training_session_id`
- `step`
- `reward_mean`
- `success_rate`
- `collision_rate`
- `file_path`
- `storage_backend`
- `created_at`
- `is_best`
- `metadata_json`

### Models List Result

`GET /api/v1/models` returned a paginated response containing model version records.

The following pagination fields were verified:

- `items`
- `total`
- `page`
- `page_size`
- `pages`
- `has_next`
- `has_previous`

The following model version response fields were verified:

- `id`
- `training_session_id`
- `checkpoint_id`
- `model_name`
- `version`
- `algorithm`
- `file_path`
- `onnx_path`
- `reward_mean`
- `success_rate`
- `collision_rate`
- `is_active`
- `created_at`
- `metadata_json`

### Invalid UUID Verification

An invalid checkpoint ID request returned:

```http
HTTP/1.1 400 Bad Request
```

Response body:

```json
{
  "error": {
    "code": "invalid_uuid",
    "message": "Invalid UUID value for 'checkpoint_id'.",
    "details": {
      "field": "checkpoint_id",
      "value": "not-a-valid-id"
    },
    "request_id": "request-id"
  }
}
```

An invalid model ID request returned:

```http
HTTP/1.1 400 Bad Request
```

Response body:

```json
{
  "error": {
    "code": "invalid_uuid",
    "message": "Invalid UUID value for 'model_id'.",
    "details": {
      "field": "model_id",
      "value": "not-a-valid-id"
    },
    "request_id": "request-id"
  }
}
```

### Checkpoints and Model Registry Verification Result

```text
Checkpoints and model registry API verification successful.

Verified checkpoint endpoints:
- POST /api/v1/checkpoints
- GET /api/v1/checkpoints
- GET /api/v1/checkpoints/{checkpoint_id}
- GET /api/v1/checkpoints/best

Verified model registry endpoints:
- POST /api/v1/models
- GET /api/v1/models
- GET /api/v1/models/{model_id}
- GET /api/v1/models/active

Verified features:
- Checkpoint uniqueness handling
- Model version uniqueness handling
- Invalid UUID handling
- Missing resource (404) handling
- Pagination response format
- OpenAPI availability
```

## Result

Phase 4G completed successfully. The backend now supports checkpoint creation, listing, detail retrieval, best checkpoint lookup, model version creation, listing, detail retrieval, active model discovery, checkpoint and model version uniqueness enforcement, artifact path metadata, model performance metadata, UUID validation, standardized error handling, conflict handling, pagination, sorting, and OpenAPI documentation.
