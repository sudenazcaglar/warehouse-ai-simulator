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


def get_first_run_id() -> str:
    _, _, runs_data = request_json("GET", "/api/v1/runs?page=1&page_size=1")

    items = runs_data.get("items", [])

    if not items:
        raise RuntimeError("No simulation run available for training API verification.")

    return items[0]["id"]


def main() -> None:
    run_id = get_first_run_id()

    _, _, training_data = request_json("GET", "/api/v1/training?page=1&page_size=5")
    assert_paginated_response(training_data, "/api/v1/training")

    start_payload = {
        "simulation_run_id": run_id,
        "algorithm": "ppo",
        "max_steps": 100000,
        "learning_rate": 0.0003,
        "batch_size": 64,
        "buffer_size": 2048,
        "checkpoint_interval": 5000,
    }

    _, _, started_training = request_json(
        "POST",
        "/api/v1/training/start",
        payload=start_payload,
        expected_status=201,
    )

    training_id = started_training.get("id")

    if not training_id:
        raise RuntimeError("Started training response did not include an id.")

    if started_training.get("status") != "running":
        raise RuntimeError(f"Training start did not create running session: {started_training}")

    _, _, training_detail = request_json("GET", f"/api/v1/training/{training_id}")

    if training_detail.get("id") != training_id:
        raise RuntimeError("Training detail response did not match created training id.")

    _, _, running_training = request_json(
        "GET",
        "/api/v1/training?status=running&page=1&page_size=10",
    )
    assert_paginated_response(running_training, "/api/v1/training?status=running")

    _, _, training_metrics = request_json(
        "GET",
        f"/api/v1/training/{training_id}/metrics?page=1&page_size=10",
    )
    assert_paginated_response(training_metrics, "/api/v1/training/{training_id}/metrics")

    _, _, stopped_training = request_json(
        "POST",
        f"/api/v1/training/{training_id}/stop",
        payload={"status": "completed"},
    )

    if stopped_training.get("status") != "completed":
        raise RuntimeError(f"Training stop did not set completed status: {stopped_training}")

    if stopped_training.get("ended_at") is None:
        raise RuntimeError("Training stop did not set ended_at.")

    _, _, repeated_stop_response = request_json(
        "POST",
        f"/api/v1/training/{training_id}/stop",
        payload={"status": "cancelled"},
        expected_status=409,
    )
    assert_error_code(repeated_stop_response, "training_already_stopped")

    _, _, invalid_training_response = request_json(
        "GET",
        "/api/v1/training/not-a-valid-id",
        expected_status=400,
    )
    assert_error_code(invalid_training_response, "invalid_uuid")

    _, _, missing_training_response = request_json(
        "GET",
        f"/api/v1/training/{uuid4()}",
        expected_status=404,
    )
    assert_error_code(missing_training_response, "not_found")

    missing_run_payload = {
        **start_payload,
        "simulation_run_id": str(uuid4()),
    }

    _, _, missing_run_response = request_json(
        "POST",
        "/api/v1/training/start",
        payload=missing_run_payload,
        expected_status=404,
    )
    assert_error_code(missing_run_response, "not_found")

    request_json("GET", "/openapi.json")

    print("Training API verification successful.")
    print("- POST /api/v1/training/start")
    print("- POST /api/v1/training/{training_id}/stop")
    print("- GET /api/v1/training")
    print("- GET /api/v1/training/{training_id}")
    print("- GET /api/v1/training/{training_id}/metrics")
    print("- invalid UUID handling")
    print("- missing resource 404 handling")
    print("- repeated stop conflict handling")
    print("- pagination response format")
    print("- OpenAPI availability")


if __name__ == "__main__":
    main()
