from enum import StrEnum


class SimulationStatus(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainingStatus(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStatus(StrEnum):
    IDLE = "idle"
    ACTIVE = "active"
    DELIVERING = "delivering"
    CHARGING = "charging"
    DISABLED = "disabled"


class AgentEventType(StrEnum):
    SPAWNED = "spawned"
    MOVED = "moved"
    PICKUP_STARTED = "pickup_started"
    PICKUP_COMPLETED = "pickup_completed"
    DELIVERY_STARTED = "delivery_started"
    DELIVERY_COMPLETED = "delivery_completed"
    REROUTE = "reroute"
    COLLISION_WARNING = "collision_warning"
    COLLISION = "collision"
    IDLE = "idle"
    CUSTOM = "custom"


class CollisionType(StrEnum):
    WALL = "wall"
    OBSTACLE = "obstacle"
    AGENT = "agent"
    SHELF = "shelf"
    UNKNOWN = "unknown"


class MetricSource(StrEnum):
    API = "api"
    UNITY = "unity"
    TRAINING = "training"
    SYSTEM = "system"
    LLM = "llm"


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    return [item.value for item in enum_class]
