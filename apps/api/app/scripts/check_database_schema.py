from sqlalchemy import inspect, text

from app.db.session import engine


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

EXPECTED_ENUM_TYPES = {
    "simulation_status",
    "training_status",
    "agent_status",
    "agent_event_type",
    "collision_type",
    "metric_source",
}


def main() -> None:
    inspector = inspect(engine)

    database_tables = set(inspector.get_table_names(schema="public"))
    application_tables = database_tables - {"alembic_version"}

    missing_tables = EXPECTED_TABLES - application_tables
    missing_alembic_table = "alembic_version" not in database_tables

    if missing_tables:
        raise RuntimeError(f"Missing database tables: {sorted(missing_tables)}")

    if missing_alembic_table:
        raise RuntimeError("Missing alembic_version table.")

    with engine.connect() as connection:
        enum_rows = connection.execute(
            text(
                """
                SELECT typname
                FROM pg_type
                WHERE typname = ANY(:enum_names)
                ORDER BY typname
                """
            ),
            {"enum_names": list(EXPECTED_ENUM_TYPES)},
        ).scalars().all()

        discovered_enums = set(enum_rows)
        missing_enums = EXPECTED_ENUM_TYPES - discovered_enums

        if missing_enums:
            raise RuntimeError(f"Missing enum types: {sorted(missing_enums)}")

        alembic_version = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()

        if not alembic_version:
            raise RuntimeError("Alembic version is empty.")

    print("Database schema verification successful.")
    print(f"Application tables: {len(application_tables)}")
    print(f"Discovered enum types: {len(discovered_enums)}")
    print(f"Alembic current revision: {alembic_version}")

    for table_name in sorted(EXPECTED_TABLES):
        columns = inspector.get_columns(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)

        print(
            f"- {table_name}: "
            f"{len(columns)} columns, "
            f"{len(foreign_keys)} foreign keys, "
            f"{len(indexes)} indexes"
        )


if __name__ == "__main__":
    main()
