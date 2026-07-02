import asyncio
import json
import os
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import websockets
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Agent, TrainingSession

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
WS_BASE_URL = os.getenv("WS_BASE_URL", "ws://127.0.0.1:8000")


def request_json(
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    expected_status: int = 200,
) -> dict[str, Any]:
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
            raw_body = response.read().decode("utf-8")
    except HTTPError as exc:
        status = exc.code
        raw_body = exc.read().decode("utf-8")

    if status != expected_status:
        raise RuntimeError(
            f"{method} {path} returned {status}, expected {expected_status}. Body: {raw_body}"
        )

    return json.loads(raw_body) if raw_body else {}


def get_training_session_ids() -> tuple[str, str]:
    with SessionLocal() as db:
        training_session = db.execute(select(TrainingSession).limit(1)).scalars().first()

        if training_session is None:
            raise RuntimeError("No training session available for WebSocket verification.")

        return str(training_session.id), str(training_session.simulation_run_id)


def get_agent_ids() -> tuple[str, str]:
    with SessionLocal() as db:
        agent = db.execute(select(Agent).limit(1)).scalars().first()

        if agent is None:
            raise RuntimeError("No agent available for WebSocket verification.")

        return str(agent.id), str(agent.simulation_run_id)


async def verify_run_metric_stream() -> None:
    training_session_id, run_id = get_training_session_ids()

    async with websockets.connect(f"{WS_BASE_URL}/ws/runs/{run_id}/metrics") as websocket:
        metric_payload = {
            "simulation_run_id": run_id,
            "training_session_id": training_session_id,
            "metric_name": "websocket_metric_verification",
            "metric_value": 99.9,
            "metric_unit": "score",
            "source": "api",
            "metadata_json": {
                "source": "api-verify-websocket",
            },
        }

        request_json(
            "POST",
            "/api/v1/metrics",
            payload=metric_payload,
            expected_status=201,
        )

        message = await asyncio.wait_for(websocket.recv(), timeout=10)
        data = json.loads(message)

        if data.get("type") != "metric":
            raise RuntimeError(f"Expected metric WebSocket payload, got: {data}")

        if data.get("data", {}).get("metric_name") != "websocket_metric_verification":
            raise RuntimeError(f"Unexpected metric payload: {data}")


async def verify_agent_event_stream() -> None:
    agent_id, run_id = get_agent_ids()

    async with websockets.connect(f"{WS_BASE_URL}/ws/agents/{agent_id}/events") as websocket:
        event_payload = {
            "simulation_run_id": run_id,
            "agent_id": agent_id,
            "step": 123456,
            "position_x": 3.25,
            "position_z": 6.5,
            "velocity": 1.2,
            "action": "websocket_event_verification",
            "reward_delta": 0.1,
            "event_type": "custom",
            "reason_code": "websocket_verification",
            "metadata_json": {
                "source": "api-verify-websocket",
            },
        }

        request_json(
            "POST",
            "/api/v1/events",
            payload=event_payload,
            expected_status=201,
        )

        message = await asyncio.wait_for(websocket.recv(), timeout=10)
        data = json.loads(message)

        if data.get("type") != "agent_event":
            raise RuntimeError(f"Expected agent_event WebSocket payload, got: {data}")

        if data.get("data", {}).get("action") != "websocket_event_verification":
            raise RuntimeError(f"Unexpected agent event payload: {data}")


async def main_async() -> None:
    await verify_run_metric_stream()
    await verify_agent_event_stream()


def main() -> None:
    asyncio.run(main_async())

    print("WebSocket stream verification successful.")
    print("- /ws/runs/{run_id}/metrics")
    print("- /ws/agents/{agent_id}/events")
    print("- metric POST broadcast")
    print("- event POST broadcast")
    print("- WebSocket payload validation")


if __name__ == "__main__":
    main()
