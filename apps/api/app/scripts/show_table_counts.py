from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models import (
    Agent,
    AgentEvent,
    Checkpoint,
    Collision,
    Delivery,
    EnvironmentConfig,
    Episode,
    LLMExplanation,
    ModelVersion,
    SimulationRun,
    SystemMetric,
    TrainingSession,
)


MODELS = [
    EnvironmentConfig,
    SimulationRun,
    TrainingSession,
    Agent,
    Episode,
    AgentEvent,
    Collision,
    Delivery,
    Checkpoint,
    ModelVersion,
    LLMExplanation,
    SystemMetric,
]


def main() -> None:
    with SessionLocal() as db:
        print("Database table counts:")

        for model in MODELS:
            count = db.execute(select(func.count()).select_from(model)).scalar_one()
            print(f"- {model.__tablename__}: {count}")


if __name__ == "__main__":
    main()
