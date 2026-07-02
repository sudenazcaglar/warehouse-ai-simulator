import json
import os
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import TrainingSession

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


def get_training_session_ids() -> tuple[str, str]:
    with SessionLocal() as db:
        training_session = db.execute(select(TrainingSession).limit(1)).scalars().first()

        if training_session is None:
            raise RuntimeError("No training session available for metrics verification.")

        return str(training_session.id), str(training_session.simulation_run_id)


def main() -> None:
    training_session_id, run_id = get_training_session_ids()

    _, _, metrics_data = request_json("GET", "/api/v1/metrics?page=1&page_size=5")
    assert_paginated_response(metrics_data, "/api/v1/metrics")

    metric_payload = {
        "simulation_run_id": run_id,
        "training_session_id": training_session_id,
        "metric_name": f"api_metric_verification_{uuid4().hex[:8]}",
        "metric_value": 42.5,
        "metric_unit": "score",
        "source": "api",
        "metadata_json": {
            "source": "api-verify-metrics",
        },
    }

    _, _, created_metric = request_json(
        "POST",
        "/api/v1/metrics",
        payload=metric_payload,
        expected_status=201,
    )

    created_metric_id = created_metric.get("id")

    if not created_metric_id:
        raise RuntimeError("Created metric response did not include an id.")

    if created_metric.get("metric_name") != metric_payload["metric_name"]:
        raise RuntimeError("Created metric did not preserve metric_name.")

    _, _, filtered_metrics = request_json(
        "GET",
        f"/api/v1/metrics?metric_name={metric_payload['metric_name']}&page=1&page_size=10",
    )
    assert_paginated_response(filtered_metrics, "/api/v1/metrics?metric_name=...")

    _, _, run_metrics = request_json(
        "GET",
        f"/api/v1/runs/{run_id}/metrics?page=1&page_size=10",
    )
    assert_paginated_response(run_metrics, "/api/v1/runs/{run_id}/metrics")

    _, _, training_metrics = request_json(
        "GET",
        f"/api/v1/training/{training_session_id}/metrics?page=1&page_size=10",
    )
    assert_paginated_response(training_metrics, "/api/v1/training/{training_id}/metrics")

    _, _, invalid_run_filter = request_json(
        "GET",
        "/api/v1/metrics?simulation_run_id=not-a-valid-id",
        expected_status=400,
    )
    assert_error_code(invalid_run_filter, "invalid_uuid")

    missing_run_payload = {
        **metric_payload,
        "simulation_run_id": str(uuid4()),
    }

    _, _, missing_run_response = request_json(
        "POST",
        "/api/v1/metrics",
        payload=missing_run_payload,
        expected_status=404,
    )
    assert_error_code(missing_run_response, "not_found")

    mismatched_payload = {
        **metric_payload,
        "simulation_run_id": str(uuid4()),
    }

    _, _, mismatch_or_missing_response = request_json(
        "POST",
        "/api/v1/metrics",
        payload=mismatched_payload,
        expected_status=404,
    )
    assert_error_code(mismatch_or_missing_response, "not_found")

    request_json("GET", "/openapi.json")

    print("Metrics API verification successful.")
    print("- POST /api/v1/metrics")
    print("- GET /api/v1/metrics")
    print("- GET /api/v1/runs/{run_id}/metrics")
    print("- GET /api/v1/training/{training_id}/metrics")
    print("- invalid UUID handling")
    print("- missing resource 404 handling")
    print("- pagination response format")
    print("- OpenAPI availability")


if __name__ == "__main__":
    main()
