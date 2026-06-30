# Database Design

This document will describe the PostgreSQL schema, data model, indexing strategy, migrations, and seed data.

## Planned Core Tables

- simulation_runs
- training_sessions
- episodes
- agents
- agent_events
- collisions
- deliveries
- checkpoints
- model_versions
- environment_configs
- llm_explanations
- system_metrics

## Design Goals

- Structured event logging
- Queryable training history
- Model version tracking
- LLM explanation storage
- Analytics-ready schema
- Migration-based database evolution

---

## Alembic Migration Workflow

The project uses Alembic for database schema migrations.

### Alembic Configuration

Alembic configuration files are located under:

```text
apps/api/alembic.ini
apps/api/alembic/
```

### Check Alembic Setup

```bash
make db-check-alembic
```

### Show Current Migration

```bash
make db-current
```

### Show Migration Heads

```bash
make db-heads
```

### Create a New Migration

```bash
make db-revision MSG="create initial schema"
```

### Apply Migrations

```bash
make db-upgrade
```

### Roll Back the Last Migration

```bash
make db-downgrade
```

### Migration Files

Migration files are stored under:

```text
apps/api/alembic/versions/
```

---

## Alembic Migration Workflow

The project uses Alembic for database schema migrations.

### Alembic Configuration

Alembic configuration files are located under:

```text
apps/api/alembic.ini
apps/api/alembic/
```

### Check Alembic Setup

```bash
make db-check-alembic
```

### Show Current Migration

```bash
make db-current
```

### Show Migration Heads

```bash
make db-heads
```

### Create a New Migration

```bash
make db-revision MSG="create initial schema"
```

### Apply Migrations

```bash
make db-upgrade
```

### Roll Back the Last Migration

```bash
make db-downgrade
```

### Migration Files

Migration files are stored under:

```text
apps/api/alembic/versions/
```
