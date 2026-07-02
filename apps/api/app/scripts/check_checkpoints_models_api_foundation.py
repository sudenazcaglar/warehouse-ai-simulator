import json
import os
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def request_json(
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    expected_status: int = 200,
) -> tuple[int, dict[str, str], dict[str, Any]]:
    body = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        url=f"{BASE_URL}{path}",
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=10) as response:
            status = response.status
            response_headers = dict(response.headers.items())
            raw_body = response.read().decode("utf-8")
    except HTTPError as exc:
        status = exc.code
        response_headers = dict(exc.headers.items())
        raw_body = exc.read().decode("utf-8")

    if status != expected_status:
        raise RuntimeError(
            f"{method} {path} returned {status}, expected {expected_status}. Body: {raw_body}"
        )

    data = json.loads(raw_body) if raw_body else {}

    return status, response_headers, data


def assert_paginated_response(data: dict[str, Any], endpoint: str) -> None:
    required_keys = {
        "items",
        "total",
        "page",
        "page_size",
        "pages",
        "has_next",
        "has_previous",
    }

    missing_keys = required_keys - set(data.keys())

    if missing_keys:
        raise RuntimeError(f"{endpoint} is missing pagination keys: {sorted(missing_keys)}")

    if not isinstance(data["items"], list):
        raise RuntimeError(f"{endpoint} items field is not a list.")


def assert_error_code(data: dict[str, Any], expected_code: str) -> None:
    code = data.get("error", {}).get("code")

    if code != expected_code:
        raise RuntimeError(f"Expected error code {expected_code}, got {code}. Body: {data}")


def get_first_training_session_id() -> str:
    _, _, training_data = request_json("GET", "/api/v1/training?page=1&page_size=1")

    items = training_data.get("items", [])

    if not items:
        raise RuntimeError("No training session available for checkpoint/model verification.")

    return items[0]["id"]


def main() -> None:
    training_session_id = get_first_training_session_id()
    unique_suffix = uuid4().hex[:8]
    checkpoint_step = 700000 + int(unique_suffix[:4], 16)

    _, _, checkpoints_data = request_json("GET", "/api/v1/checkpoints?page=1&page_size=5")
    assert_paginated_response(checkpoints_data, "/api/v1/checkpoints")

    checkpoint_payload = {
        "training_session_id": training_session_id,
        "step": checkpoint_step,
        "reward_mean": 88.5,
        "success_rate": 0.92,
        "collision_rate": 0.03,
        "file_path": f"s3://warehouse-ai/checkpoints/api-check-{unique_suffix}.pt",
        "storage_backend": "minio",
        "is_best": True,
        "metadata_json": {
            "source": "api-verify-checkpoints-models",
        },
    }

    _, _, created_checkpoint = request_json(
        "POST",
        "/api/v1/checkpoints",
        payload=checkpoint_payload,
        expected_status=201,
    )

    checkpoint_id = created_checkpoint.get("id")

    if not checkpoint_id:
        raise RuntimeError("Created checkpoint response did not include an id.")

    if not created_checkpoint.get("is_best"):
        raise RuntimeError("Created checkpoint did not preserve is_best=true.")

    _, _, checkpoint_detail = request_json("GET", f"/api/v1/checkpoints/{checkpoint_id}")

    if checkpoint_detail.get("id") != checkpoint_id:
        raise RuntimeError("Checkpoint detail response did not match created checkpoint id.")

    _, _, best_checkpoint = request_json(
        "GET",
        f"/api/v1/checkpoints/best?training_session_id={training_session_id}",
    )

    if best_checkpoint.get("id") != checkpoint_id:
        raise RuntimeError("Best checkpoint did not return the newly created best checkpoint.")

    _, _, duplicate_checkpoint_response = request_json(
        "POST",
        "/api/v1/checkpoints",
        payload=checkpoint_payload,
        expected_status=409,
    )
    assert_error_code(duplicate_checkpoint_response, "checkpoint_step_exists")

    _, _, models_data = request_json("GET", "/api/v1/models?page=1&page_size=5")
    assert_paginated_response(models_data, "/api/v1/models")

    model_name = f"api-model-{unique_suffix}"
    model_version = "v1.0.0"

    model_payload = {
        "training_session_id": training_session_id,
        "checkpoint_id": checkpoint_id,
        "model_name": model_name,
        "version": model_version,
        "algorithm": "ppo",
        "file_path": f"s3://warehouse-ai/models/{model_name}/{model_version}/model.pt",
        "onnx_path": f"s3://warehouse-ai/models/{model_name}/{model_version}/model.onnx",
        "reward_mean": 88.5,
        "success_rate": 0.92,
        "collision_rate": 0.03,
        "is_active": True,
        "metadata_json": {
            "source": "api-verify-checkpoints-models",
        },
    }

    _, _, created_model = request_json(
        "POST",
        "/api/v1/models",
        payload=model_payload,
        expected_status=201,
    )

    model_id = created_model.get("id")

    if not model_id:
        raise RuntimeError("Created model response did not include an id.")

    if not created_model.get("is_active"):
        raise RuntimeError("Created model did not preserve is_active=true.")

    _, _, model_detail = request_json("GET", f"/api/v1/models/{model_id}")

    if model_detail.get("id") != model_id:
        raise RuntimeError("Model detail response did not match created model id.")

    _, _, active_models = request_json(
        "GET",
        f"/api/v1/models/active?model_name={model_name}&page=1&page_size=10",
    )
    assert_paginated_response(active_models, "/api/v1/models/active")

    active_model_ids = {item["id"] for item in active_models.get("items", [])}

    if model_id not in active_model_ids:
        raise RuntimeError("Active models endpoint did not include created active model.")

    _, _, duplicate_model_response = request_json(
        "POST",
        "/api/v1/models",
        payload=model_payload,
        expected_status=409,
    )
    assert_error_code(duplicate_model_response, "model_version_exists")

    _, _, invalid_checkpoint_response = request_json(
        "GET",
        "/api/v1/checkpoints/not-a-valid-id",
        expected_status=400,
    )
    assert_error_code(invalid_checkpoint_response, "invalid_uuid")

    _, _, invalid_model_response = request_json(
        "GET",
        "/api/v1/models/not-a-valid-id",
        expected_status=400,
    )
    assert_error_code(invalid_model_response, "invalid_uuid")

    _, _, missing_checkpoint_response = request_json(
        "GET",
        f"/api/v1/checkpoints/{uuid4()}",
        expected_status=404,
    )
    assert_error_code(missing_checkpoint_response, "not_found")

    _, _, missing_model_response = request_json(
        "GET",
        f"/api/v1/models/{uuid4()}",
        expected_status=404,
    )
    assert_error_code(missing_model_response, "not_found")

    request_json("GET", "/openapi.json")

    print("Checkpoints and model registry API verification successful.")
    print("- POST /api/v1/checkpoints")
    print("- GET /api/v1/checkpoints")
    print("- GET /api/v1/checkpoints/{checkpoint_id}")
    print("- GET /api/v1/checkpoints/best")
    print("- checkpoint uniqueness handling")
    print("- POST /api/v1/models")
    print("- GET /api/v1/models")
    print("- GET /api/v1/models/{model_id}")
    print("- GET /api/v1/models/active")
    print("- model version uniqueness handling")
    print("- invalid UUID handling")
    print("- missing resource 404 handling")
    print("- pagination response format")
    print("- OpenAPI availability")


if __name__ == "__main__":
    main()
