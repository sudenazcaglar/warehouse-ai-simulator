"""SQLAlchemy ORM models.

Importing this package registers all model classes with SQLAlchemy metadata so
Alembic can discover them during migration autogeneration.
"""

from app.models.agent import Agent
from app.models.agent_event import AgentEvent
from app.models.checkpoint import Checkpoint
from app.models.collision import Collision
from app.models.delivery import Delivery
from app.models.environment_config import EnvironmentConfig
from app.models.episode import Episode
from app.models.llm_explanation import LLMExplanation
from app.models.model_version import ModelVersion
from app.models.simulation_run import SimulationRun
from app.models.system_metric import SystemMetric
from app.models.training_session import TrainingSession

__all__ = [
    "Agent",
    "AgentEvent",
    "Checkpoint",
    "Collision",
    "Delivery",
    "EnvironmentConfig",
    "Episode",
    "LLMExplanation",
    "ModelVersion",
    "SimulationRun",
    "SystemMetric",
    "TrainingSession",
]
