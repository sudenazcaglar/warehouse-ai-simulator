# Explainable Multi-Agent Warehouse Robot Training Simulator

A production-oriented AI engineering project that simulates, trains, monitors, and explains multi-agent warehouse robot behavior using Unity ML-Agents, reinforcement learning, Docker, PostgreSQL, real-time dashboards, and LLM-based explanations.

## Project Goal

The goal of this project is to build an end-to-end warehouse robot simulation system where autonomous agents are trained in Unity using reinforcement learning, monitored through a real-time web dashboard, stored in a professional database architecture, deployed with Docker, and explained through an LLM-powered reasoning layer.

This project is designed to demonstrate skills in:

- Reinforcement Learning
- Unity ML-Agents
- Multi-Agent Simulation
- Data Engineering
- PostgreSQL Database Design
- FastAPI Backend Development
- React / Next.js Dashboard Development
- Docker and Deployment
- Real-Time Monitoring
- LLM Integration
- Model Checkpointing and Registry
- Real-World AI System Design

## High-Level Architecture

```text
Unity Simulation
    ↓
ML-Agents Training Worker
    ↓
Checkpoint / Model Registry
    ↓
FastAPI Backend
    ↓
PostgreSQL + Redis + Object Storage
    ↓
React Dashboard
    ↓
LLM Explanation Layer
```

## Main Features

- Unity-based warehouse simulation environment
- Single-agent and multi-agent robot training
- PPO-based reinforcement learning with Unity ML-Agents
- Training metrics and event logging
- PostgreSQL-backed structured data model
- FastAPI backend for simulation, metrics, checkpoints, and explanations
- Real-time dashboard with WebSocket support
- Docker Compose based local and production environments
- Cloud GPU training workflow
- Live simulation streaming
- LLM-based explanation of robot decisions
- Real-world warehouse integration design

## Repository Structure

```text
warehouse-ai-simulator/
├── apps/
│   ├── api/
│   ├── dashboard/
│   └── llm-service/
├── unity/
│   └── WarehouseSimulator/
├── training/
│   ├── configs/
│   ├── scripts/
│   ├── checkpoints/
│   └── notebooks/
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   ├── grafana/
│   └── prometheus/
├── database/
│   ├── migrations/
│   └── seeds/
├── docs/
├── media/
└── docker-compose.yml
```

## Project Phases

1. Project foundation and repository setup
2. Docker-based development infrastructure
3. Professional database architecture
4. FastAPI backend
5. Unity warehouse simulation MVP
6. ML-Agents single-agent training
7. Checkpointing and model registry
8. Real-time dashboard
9. Visual polish and cinematic demo mode
10. Multi-agent training
11. Live streaming
12. LLM explanation layer
13. Monitoring and observability
14. Cloud GPU training pipeline
15. Production deployment
16. Real-world integration design
17. Testing and CI/CD
18. Demo, documentation, and final showcase

## Current Status

Project foundation phase is in progress.

## Planned System Components

| Component          | Purpose                                                                           |
| ------------------ | --------------------------------------------------------------------------------- |
| Unity Simulation   | Warehouse environment, robots, shelves, delivery zones, obstacles                 |
| ML-Agents Training | PPO-based reinforcement learning and model export                                 |
| FastAPI Backend    | API layer for runs, events, metrics, checkpoints, and explanations                |
| PostgreSQL         | Structured storage for simulation runs, agent events, metrics, and model metadata |
| Redis              | Cache, queue, and real-time coordination layer                                    |
| Object Storage     | Model artifacts, ONNX files, checkpoints, and training outputs                    |
| React Dashboard    | Real-time monitoring, model registry, training charts, and live stream            |
| LLM Service        | Natural language explanations of robot behavior                                   |
| Docker Compose     | Reproducible local and production-like deployment                                 |
| Monitoring Stack   | Prometheus and Grafana observability                                              |

## Target Outcome

The final project will be a complete AI engineering showcase demonstrating how a reinforcement learning simulation can be developed, monitored, explained, containerized, and deployed with production-oriented software engineering practices.

## License

MIT License

## Docker Development Quick Start

The project includes a Docker Compose based local development environment.

Start all services:

```bash
docker compose up --build -d
```

Check running services:

```bash
docker compose ps
```

Main local URLs:

| Service       | URL                          |
| ------------- | ---------------------------- |
| Dashboard     | <http://localhost:3000>      |
| API Docs      | <http://localhost:8000/docs> |
| Nginx Gateway | <http://localhost:8080>      |
| MinIO Console | <http://localhost:9001>      |
| Prometheus    | <http://localhost:9090>      |
| Grafana       | <http://localhost:3001>      |
| TensorBoard   | <http://localhost:6006>      |

For details, see [Docker Development Environment](docs/docker.md).

## Developer Workflow

Common development commands are available through the project Makefile.

```bash
make doctor
make up
make ps
make health
make logs
make down
```

The Docker workflow is documented in [docs/docker.md](docs/docker.md).

## Developer Workflow

Common development commands are available through the project Makefile.

```bash
make doctor
make up
make ps
make health
make logs
make down
```

The Docker workflow is documented in [docs/docker.md](docs/docker.md).
