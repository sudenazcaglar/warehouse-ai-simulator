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


EXPECTED_MINIMUM_COUNTS = {
    EnvironmentConfig: 1,
    SimulationRun: 1,
    TrainingSession: 1,
    Agent: 3,
    Episode: 5,
    AgentEvent: 50,
    Collision: 3,
    Delivery: 5,
    Checkpoint: 3,
    ModelVersion: 2,
    LLMExplanation: 3,
    SystemMetric: 20,
}


def count_rows(model: type) -> int:
    with SessionLocal() as db:
        return int(db.execute(select(func.count()).select_from(model)).scalar_one())


def main() -> None:
    print("Checking seed/demo data counts...")

    for model, minimum_count in EXPECTED_MINIMUM_COUNTS.items():
        count = count_rows(model)

        if count < minimum_count:
            raise RuntimeError(
                f"{model.__tablename__} has {count} rows, expected at least {minimum_count}."
            )

        print(f"OK: {model.__tablename__}: {count} rows")

    print("Seed/demo data verification successful.")


if __name__ == "__main__":
    main()
