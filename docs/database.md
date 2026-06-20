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
