import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("warehouse_api.websocket")


class WebSocketConnectionManager:
    def __init__(self) -> None:
        self.run_metric_connections: dict[str, set[WebSocket]] = defaultdict(set)
        self.agent_event_connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect_run_metrics(self, run_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.run_metric_connections[run_id].add(websocket)

        logger.info(
            "websocket_connected stream=run_metrics run_id=%s active_connections=%s",
            run_id,
            len(self.run_metric_connections[run_id]),
        )

    def disconnect_run_metrics(self, run_id: str, websocket: WebSocket) -> None:
        self.run_metric_connections[run_id].discard(websocket)

        if not self.run_metric_connections[run_id]:
            self.run_metric_connections.pop(run_id, None)

        logger.info(
            "websocket_disconnected stream=run_metrics run_id=%s",
            run_id,
        )

    async def broadcast_run_metric(self, run_id: str, payload: dict[str, Any]) -> None:
        connections = list(self.run_metric_connections.get(run_id, set()))

        if not connections:
            return

        logger.info(
            "websocket_broadcast stream=run_metrics run_id=%s connections=%s",
            run_id,
            len(connections),
        )

        for websocket in connections:
            try:
                await websocket.send_json(payload)
            except Exception:
                logger.exception(
                    "websocket_broadcast_failed stream=run_metrics run_id=%s",
                    run_id,
                )
                self.disconnect_run_metrics(run_id, websocket)

    async def connect_agent_events(self, agent_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.agent_event_connections[agent_id].add(websocket)

        logger.info(
            "websocket_connected stream=agent_events agent_id=%s active_connections=%s",
            agent_id,
            len(self.agent_event_connections[agent_id]),
        )

    def disconnect_agent_events(self, agent_id: str, websocket: WebSocket) -> None:
        self.agent_event_connections[agent_id].discard(websocket)

        if not self.agent_event_connections[agent_id]:
            self.agent_event_connections.pop(agent_id, None)

        logger.info(
            "websocket_disconnected stream=agent_events agent_id=%s",
            agent_id,
        )

    async def broadcast_agent_event(self, agent_id: str, payload: dict[str, Any]) -> None:
        connections = list(self.agent_event_connections.get(agent_id, set()))

        if not connections:
            return

        logger.info(
            "websocket_broadcast stream=agent_events agent_id=%s connections=%s",
            agent_id,
            len(connections),
        )

        for websocket in connections:
            try:
                await websocket.send_json(payload)
            except Exception:
                logger.exception(
                    "websocket_broadcast_failed stream=agent_events agent_id=%s",
                    agent_id,
                )
                self.disconnect_agent_events(agent_id, websocket)


websocket_manager = WebSocketConnectionManager()
