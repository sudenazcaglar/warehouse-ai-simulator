from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_db, validate_uuid
from app.api.errors import APIError
from app.repositories import agents as agent_repository
from app.repositories import runs as run_repository
from app.schemas.common import ModuleStatusResponse
from app.services.websocket_manager import websocket_manager

router = APIRouter(prefix="/stream", tags=["stream"])
ws_router = APIRouter(tags=["websocket"])


@router.get("/status", response_model=ModuleStatusResponse)
def stream_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="stream",
        status="available",
        detail="WebSocket stream endpoints are available under /ws.",
        metadata={
            "run_metrics": "/ws/runs/{run_id}/metrics",
            "agent_events": "/ws/agents/{agent_id}/events",
        },
    )


@ws_router.websocket("/ws/runs/{run_id}/metrics")
async def run_metrics_stream(
    websocket: WebSocket,
    run_id: str,
    db: Session = Depends(get_db),
) -> None:
    try:
        parsed_run_id = validate_uuid(run_id, "run_id")
        run_repository.require_run_by_id(db, parsed_run_id)
    except APIError:
        await websocket.close(code=1008)
        return

    connection_key = str(parsed_run_id)
    await websocket_manager.connect_run_metrics(connection_key, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect_run_metrics(connection_key, websocket)


@ws_router.websocket("/ws/agents/{agent_id}/events")
async def agent_events_stream(
    websocket: WebSocket,
    agent_id: str,
    db: Session = Depends(get_db),
) -> None:
    try:
        parsed_agent_id = validate_uuid(agent_id, "agent_id")
        agent_repository.require_agent_by_id(db, parsed_agent_id)
    except APIError:
        await websocket.close(code=1008)
        return

    connection_key = str(parsed_agent_id)
    await websocket_manager.connect_agent_events(connection_key, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect_agent_events(connection_key, websocket)
