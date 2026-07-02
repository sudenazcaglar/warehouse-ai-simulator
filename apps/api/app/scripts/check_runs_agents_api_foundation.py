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


def main() -> None:
    _, _, runs_data = request_json("GET", "/api/v1/runs?page=1&page_size=5")
    assert_paginated_response(runs_data, "/api/v1/runs")

    _, _, agents_data = request_json("GET", "/api/v1/agents?page=1&page_size=5")
    assert_paginated_response(agents_data, "/api/v1/agents")

    _, headers, invalid_run_data = request_json(
        "GET",
        "/api/v1/runs/not-a-valid-id",
        expected_status=400,
    )
    assert_error_code(invalid_run_data, "invalid_uuid")

    normalized_headers = {key.lower(): value for key, value in headers.items()}

    if "x-request-id" not in normalized_headers:
        raise RuntimeError(
            "Invalid UUID response did not include X-Request-ID header. "
            f"Observed headers: {sorted(headers.keys())}"
        )

    missing_run_id = uuid4()
    _, _, missing_run_data = request_json(
        "GET",
        f"/api/v1/runs/{missing_run_id}",
        expected_status=404,
    )
    assert_error_code(missing_run_data, "not_found")

    create_payload = {
        "run_name": f"api-verify-run-{uuid4().hex[:8]}",
        "environment_name": "WarehouseSimulator-API",
        "agent_count": 1,
        "map_version": "2026.api",
        "config_json": {
            "source": "api-verify-runs-agents",
        },
    }

    _, _, created_run = request_json(
        "POST",
        "/api/v1/runs",
        payload=create_payload,
        expected_status=201,
    )

    created_run_id = created_run.get("id")

    if not created_run_id:
        raise RuntimeError("Created run response did not include an id.")

    _, _, run_detail = request_json("GET", f"/api/v1/runs/{created_run_id}")

    if run_detail.get("id") != created_run_id:
        raise RuntimeError("Run detail response did not match created run id.")

    _, _, run_agents_data = request_json(
        "GET",
        f"/api/v1/runs/{created_run_id}/agents",
    )
    assert_paginated_response(run_agents_data, f"/api/v1/runs/{created_run_id}/agents")

    _, _, filtered_runs = request_json(
        "GET",
        "/api/v1/runs?status=created&page=1&page_size=10",
    )
    assert_paginated_response(filtered_runs, "/api/v1/runs?status=created")

    _, _, filtered_agents = request_json(
        "GET",
        "/api/v1/agents?status=active&page=1&page_size=10",
    )
    assert_paginated_response(filtered_agents, "/api/v1/agents?status=active")

    request_json("GET", "/openapi.json")

    print("Runs and agents API verification successful.")
    print("- GET /api/v1/runs")
    print("- POST /api/v1/runs")
    print("- GET /api/v1/runs/{run_id}")
    print("- GET /api/v1/runs/{run_id}/agents")
    print("- GET /api/v1/agents")
    print("- invalid UUID handling")
    print("- missing resource 404 handling")
    print("- pagination response format")
    print("- OpenAPI availability")


if __name__ == "__main__":
    main()
