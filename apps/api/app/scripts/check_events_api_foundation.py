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


def find_first_agent_with_run() -> tuple[str, str]:
    _, _, agents_data = request_json("GET", "/api/v1/agents?page=1&page_size=1")

    items = agents_data.get("items", [])

    if not items:
        raise RuntimeError("No agents available for event API verification.")

    agent = items[0]
    return agent["id"], agent["simulation_run_id"]


def find_mismatched_run(agent_run_id: str) -> str | None:
    _, _, runs_data = request_json("GET", "/api/v1/runs?page=1&page_size=20")

    for run in runs_data.get("items", []):
        if run["id"] != agent_run_id:
            return run["id"]

    return None


def main() -> None:
    agent_id, run_id = find_first_agent_with_run()

    _, _, events_data = request_json("GET", "/api/v1/events?page=1&page_size=5")
    assert_paginated_response(events_data, "/api/v1/events")

    event_payload = {
        "simulation_run_id": run_id,
        "agent_id": agent_id,
        "step": 98765,
        "position_x": 12.5,
        "position_z": 7.25,
        "velocity": 1.75,
        "action": "api_event_ingestion_check",
        "reward_delta": 0.25,
        "event_type": "moved",
        "reason_code": "api_verification",
        "metadata_json": {
            "source": "api-verify-events",
        },
    }

    _, _, created_event = request_json(
        "POST",
        "/api/v1/events",
        payload=event_payload,
        expected_status=201,
    )

    created_event_id = created_event.get("id")

    if not created_event_id:
        raise RuntimeError("Created event response did not include an id.")

    if created_event.get("event_type") != "moved":
        raise RuntimeError("Created event did not preserve event_type.")

    _, _, filtered_events = request_json(
        "GET",
        "/api/v1/events?event_type=moved&page=1&page_size=10",
    )
    assert_paginated_response(filtered_events, "/api/v1/events?event_type=moved")

    _, _, run_events = request_json(
        "GET",
        f"/api/v1/runs/{run_id}/events?page=1&page_size=10",
    )
    assert_paginated_response(run_events, "/api/v1/runs/{run_id}/events")

    _, _, agent_timeline = request_json(
        "GET",
        f"/api/v1/agents/{agent_id}/timeline?page=1&page_size=10",
    )
    assert_paginated_response(agent_timeline, "/api/v1/agents/{agent_id}/timeline")

    timeline_items = agent_timeline.get("items", [])

    if timeline_items:
        timestamps = [item["timestamp"] for item in timeline_items]

        if timestamps != sorted(timestamps):
            raise RuntimeError("Agent timeline is not sorted in ascending timestamp order.")

    _, _, invalid_run_filter = request_json(
        "GET",
        "/api/v1/events?simulation_run_id=not-a-valid-id",
        expected_status=400,
    )
    assert_error_code(invalid_run_filter, "invalid_uuid")

    missing_run_payload = {
        **event_payload,
        "simulation_run_id": str(uuid4()),
    }

    _, _, missing_run_response = request_json(
        "POST",
        "/api/v1/events",
        payload=missing_run_payload,
        expected_status=404,
    )
    assert_error_code(missing_run_response, "not_found")

    mismatched_run_id = find_mismatched_run(run_id)

    if mismatched_run_id is not None:
        mismatch_payload = {
            **event_payload,
            "simulation_run_id": mismatched_run_id,
        }

        _, _, mismatch_response = request_json(
            "POST",
            "/api/v1/events",
            payload=mismatch_payload,
            expected_status=409,
        )
        assert_error_code(mismatch_response, "agent_run_mismatch")

    request_json("GET", "/openapi.json")

    print("Events API verification successful.")
    print("- POST /api/v1/events")
    print("- GET /api/v1/events")
    print("- GET /api/v1/events?event_type=moved")
    print("- GET /api/v1/agents/{agent_id}/timeline")
    print("- GET /api/v1/runs/{run_id}/events")
    print("- invalid UUID handling")
    print("- missing resource 404 handling")
    print("- run-agent relationship validation")
    print("- pagination response format")
    print("- timeline ascending ordering")
    print("- OpenAPI availability")


if __name__ == "__main__":
    main()
