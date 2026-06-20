# Project Roadmap

## Phase 1 — Project Foundation

Status: In Progress

Goals:

- Create professional repository structure
- Define project scope
- Prepare documentation skeleton
- Add issue and pull request templates
- Prepare initial architecture documentation

Deliverables:

- GitHub repository
- README
- Folder structure
- Roadmap
- Architecture draft
- Initial commit

## Phase 2 — Dockerized Development Foundation

Goals:

- Add Docker Compose
- Containerize API, dashboard, PostgreSQL, Redis, MinIO, Prometheus, Grafana, and TensorBoard
- Prepare development and production environment structure

## Phase 3 — Database Architecture

Goals:

- Design PostgreSQL schema
- Add Alembic migrations
- Add seed data
- Prepare ERD documentation

## Phase 4 — FastAPI Backend

Goals:

- Build core API modules
- Add event ingestion
- Add training session APIs
- Add checkpoint APIs
- Add WebSocket support

## Phase 5 — Unity Simulation MVP

Goals:

- Create warehouse simulation scene
- Add robot prefab
- Add shelves, delivery zones, obstacles, and basic movement
- Send events to backend

## Phase 6 — Single-Agent RL Training

Goals:

- Integrate Unity ML-Agents
- Define observations, actions, and rewards
- Train first PPO model
- Export ONNX model

## Phase 7 — Checkpoint and Model Registry

Goals:

- Track checkpoints
- Store metadata in database
- Upload model artifacts
- Compare model versions

## Phase 8 — Real-Time Dashboard

Goals:

- Build dashboard overview
- Add metrics charts
- Add agent timeline
- Add checkpoint viewer

## Phase 9 — Visual Showcase

Goals:

- Improve Unity visuals
- Add cinematic camera
- Add route effects
- Add demo recording mode

## Phase 10 — Multi-Agent Training

Goals:

- Add multiple robots
- Add shared task pool
- Add traffic and congestion metrics
- Train multi-agent policy

## Phase 11 — Live Streaming

Goals:

- Stream Unity simulation to dashboard
- Add HLS or WebRTC support
- Display real-time event feed next to video

## Phase 12 — LLM Explanation Layer

Goals:

- Explain robot decisions from event logs
- Add episode summaries
- Add failure analysis
- Add dashboard question-answer panel

## Phase 13 — Observability

Goals:

- Add Prometheus metrics
- Add Grafana dashboards
- Add structured logging

## Phase 14 — Cloud Training

Goals:

- Prepare cloud GPU training workflow
- Add checkpoint backup
- Add resume training documentation

## Phase 15 — Production Deploy

Goals:

- Deploy dashboard and API
- Configure HTTPS
- Add production Docker Compose
- Add backup and rollback strategy

## Phase 16 — Real-World Integration Design

Goals:

- Document how the trained model could integrate with real warehouse systems
- Define safety controller architecture
- Explain sim-to-real limitations

## Phase 17 — Testing and CI/CD

Goals:

- Add backend tests
- Add frontend checks
- Add GitHub Actions
- Add Docker build validation

## Phase 18 — Final Showcase

Goals:

- Create demo video
- Polish README
- Add screenshots
- Prepare technical presentation
- Prepare CV and LinkedIn descriptions
