import app.models  # noqa: F401
from app.db.base import Base


EXPECTED_TABLES = {
    "environment_configs",
    "simulation_runs",
    "training_sessions",
    "episodes",
    "agents",
    "agent_events",
    "collisions",
    "deliveries",
    "checkpoints",
    "model_versions",
    "llm_explanations",
    "system_metrics",
}


def main() -> None:
    discovered_tables = set(Base.metadata.tables.keys())

    missing_tables = EXPECTED_TABLES - discovered_tables
    extra_tables = discovered_tables - EXPECTED_TABLES

    if missing_tables:
        raise RuntimeError(f"Missing expected tables: {sorted(missing_tables)}")

    if extra_tables:
        raise RuntimeError(f"Unexpected extra tables: {sorted(extra_tables)}")

    print("SQLAlchemy model metadata loaded successfully.")
    print(f"Discovered tables: {len(discovered_tables)}")

    for table in Base.metadata.sorted_tables:
        print(
            f"- {table.name}: "
            f"{len(table.columns)} columns, "
            f"{len(table.foreign_keys)} foreign keys, "
            f"{len(table.indexes)} indexes"
        )


if __name__ == "__main__":
    main()
