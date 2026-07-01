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

---

## ORM Model Architecture

The database model layer is implemented using SQLAlchemy 2.0 typed ORM models.

### Current ORM Tables

| Table                 | Purpose                                                      |
| --------------------- | ------------------------------------------------------------ |
| `environment_configs` | Stores reusable simulation and training environment settings |
| `simulation_runs`     | Represents Unity simulation executions                       |
| `training_sessions`   | Represents ML-Agents / PPO training sessions                 |
| `episodes`            | Stores reinforcement learning episode-level summaries        |
| `agents`              | Represents robots inside a simulation run                    |
| `agent_events`        | Stores robot movement, decision, reward, and event logs      |
| `collisions`          | Stores collision events                                      |
| `deliveries`          | Stores pickup and delivery task outcomes                     |
| `checkpoints`         | Stores training checkpoint metadata                          |
| `model_versions`      | Stores trained model version metadata                        |
| `llm_explanations`    | Stores LLM-generated explanations for agent events           |
| `system_metrics`      | Stores time-series system and training metrics               |

## Relationship Overview

```text
environment_configs
├── simulation_runs
└── training_sessions

simulation_runs
├── training_sessions
├── episodes
├── agents
├── agent_events
├── collisions
├── deliveries
└── system_metrics

training_sessions
├── episodes
├── checkpoints
├── model_versions
└── system_metrics

agents
├── agent_events
├── collisions
└── deliveries

agent_events
└── llm_explanations

checkpoints
└── model_versions
```

## JSONB Usage

JSONB fields are used for flexible metadata that may vary across simulation, training, and LLM workflows.

Examples include:

- Simulation configuration snapshots
- Unity event payloads
- Training hyperparameter metadata
- Checkpoint artifact metadata
- LLM prompt and context metadata

## Model Metadata Verification

```bash
make db-check-models
```

---

## Initial Schema Migration

The initial database schema is generated from the SQLAlchemy ORM models using Alembic autogeneration.

### Generate the Initial Migration

```bash
make db-revision MSG="create initial database schema"
```

### Apply the Initial Migration

```bash
make db-upgrade
```

### Verify the Current Revision

```bash
make db-current
make db-heads
```

### Verify the Database Schema

```bash
make db-check-schema
```

### Inspect PostgreSQL Tables

```bash
docker compose exec postgres psql -U warehouse_user -d warehouse_ai -c "\dt"
```

### Inspect PostgreSQL Enum Types

```bash
docker compose exec postgres psql -U warehouse_user -d warehouse_ai -c "\dT"
```

## Initial Schema Result

The initial schema creates the following application tables:

- `environment_configs`
- `simulation_runs`
- `training_sessions`
- `episodes`
- `agents`
- `agent_events`
- `collisions`
- `deliveries`
- `checkpoints`
- `model_versions`
- `llm_explanations`
- `system_metrics`

Alembic also creates the following internal table:

- `alembic_version`

## Schema Features

The generated schema includes:

- UUID primary keys
- Foreign key relationships
- PostgreSQL enum types
- JSONB metadata fields
- Indexes
- Unique constraints
- Timestamp fields

## Index Count Note

PostgreSQL automatically creates physical indexes to enforce unique constraints. As a result, database-level index inspection may report more indexes than SQLAlchemy `table.indexes`, which counts only explicitly declared `Index(...)` objects.

This behavior is expected for tables with unique constraints, including:

- `environment_configs`
- `agents`
- `checkpoints`
- `episodes`
- `model_versions`
