# System Architecture

## Overview

This project is designed as a modular AI engineering system that combines simulation, reinforcement learning, data engineering, backend services, real-time dashboards, Dockerized deployment, and LLM-based explanation.

The system is divided into the following major components:

1. Unity Simulation Environment
2. ML-Agents Training Worker
3. FastAPI Backend
4. PostgreSQL Database
5. Redis Cache / Queue
6. Object Storage for Models and Checkpoints
7. React / Next.js Dashboard
8. LLM Explanation Service
9. Monitoring and Observability Stack
10. Streaming Layer
11. Production-like Nginx Gateway

---

## High-Level Architecture Diagram

```mermaid
flowchart LR
    Unity[Unity Warehouse Simulation] -->|Events / Metrics| API[FastAPI Backend]
    Trainer[ML-Agents Training Worker] -->|Training Metrics| API
    Trainer -->|Checkpoints / ONNX Models| Storage[MinIO Object Storage]

    API -->|Structured Data| Postgres[(PostgreSQL)]
    API -->|Cache / Queue| Redis[(Redis)]
    API -->|Model Metadata| Storage

    API -->|REST / WebSocket| Dashboard[React Dashboard]
    Dashboard -->|User Questions| LLM[LLM Explanation Service]
    LLM -->|Event Context Query| API

    API -->|Metrics| Prometheus[Prometheus]
    Prometheus --> Grafana[Grafana]

    Trainer --> TensorBoard[TensorBoard]

    Nginx[Nginx Gateway] --> Dashboard
    Nginx --> API
```

---

## Dockerized Development Architecture

```mermaid
flowchart TB
    subgraph DockerNetwork[warehouse-network]
        API[api container]
        Dashboard[dashboard container]
        Postgres[(postgres container)]
        Redis[(redis container)]
        MinIO[(minio container)]
        Prometheus[prometheus container]
        Grafana[grafana container]
        TensorBoard[tensorboard container]
        Nginx[nginx container]
    end

    Browser[Developer Browser] -->|localhost:3000| Dashboard
    Browser -->|localhost:8000/docs| API
    Browser -->|localhost:8080| Nginx
    Browser -->|localhost:9001| MinIO
    Browser -->|localhost:9090| Prometheus
    Browser -->|localhost:3001| Grafana
    Browser -->|localhost:6006| TensorBoard

    Dashboard --> API
    Nginx --> Dashboard
    Nginx --> API
    API --> Postgres
    API --> Redis
    API --> MinIO
    Prometheus --> API
    Grafana --> Prometheus
```

---

## Production-Like Architecture

```mermaid
flowchart TB
    User[User / Browser] -->|HTTP| NginxProd[Nginx Gateway]

    subgraph ProdNetwork[warehouse-prod-network]
        NginxProd --> DashboardProd[Static Dashboard served by Nginx]
        NginxProd --> APIProd[FastAPI API without reload]

        APIProd --> PostgresProd[(PostgreSQL)]
        APIProd --> RedisProd[(Redis)]
        APIProd --> MinIOProd[(MinIO Object Storage)]

        PrometheusProd[Prometheus - optional profile] --> APIProd
        GrafanaProd[Grafana - optional profile] --> PrometheusProd
    end
```

---

## High-Level Data Flow

```text
Unity Simulation
    ↓ event logs / metrics
FastAPI Backend
    ↓ structured persistence
PostgreSQL
    ↓ real-time updates
React Dashboard
    ↓ explanation requests
LLM Explanation Service
```

---

## Training Flow

```text
Unity Environment
    ↓ observations
ML-Agents PPO Trainer
    ↓ trained policy
Checkpoint Files
    ↓ metadata
Model Registry
    ↓ deployment / evaluation
Unity Inference Mode
```

---

## Live Monitoring Flow

```text
Unity Simulation
    ↓ event stream
FastAPI WebSocket
    ↓ live metrics
React Dashboard
```

---

## LLM Explanation Flow

```text
Agent Event Logs
    ↓
FastAPI Query Layer
    ↓
LLM Explanation Service
    ↓
Natural Language Explanation
    ↓
Dashboard
```

---

## Planned Services

| Service | Responsibility |
|---|---|
| api | Core backend service built with FastAPI |
| dashboard | Web dashboard for monitoring and model management |
| llm-service | Explanation service for interpreting robot events |
| postgres | Main relational database |
| redis | Cache and lightweight queue |
| minio | Object storage for checkpoints and model artifacts |
| prometheus | Metrics collection |
| grafana | Monitoring dashboards |
| tensorboard | Training visualization |
| nginx | Reverse proxy and production-like gateway |

---

## Development Modes

The project supports multiple Docker execution modes.

| Mode | Command | Purpose |
|---|---|---|
| Core development | `make up-core` | Runs lightweight local stack |
| Full development | `make up-full` | Runs core services, observability, and training tools |
| Production-like | `make prod-up` | Runs production-like stack with static dashboard and Nginx gateway |

---

## Core Design Principles

- Modular architecture
- Docker-first development
- Reproducible training
- Structured event logging
- Explainable AI layer
- Real-time observability
- Production-oriented deployment
- Clear separation between simulation, training, backend, dashboard, and explanation services
- Development and production-like environment separation
