from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import delete
from sqlalchemy.orm import Session

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
from app.models.enums import (
    AgentEventType,
    AgentStatus,
    CollisionType,
    MetricSource,
    SimulationStatus,
    TrainingStatus,
)


def clear_database(db: Session) -> None:
    """Delete demo data in dependency-safe order."""

    models = [
        LLMExplanation,
        ModelVersion,
        Checkpoint,
        Delivery,
        Collision,
        AgentEvent,
        SystemMetric,
        Episode,
        TrainingSession,
        Agent,
        SimulationRun,
        EnvironmentConfig,
    ]

    for model in models:
        db.execute(delete(model))

    db.commit()


def seed_database(db: Session) -> None:
    now = datetime.now(timezone.utc)

    environment_config = EnvironmentConfig(
        name="small-warehouse-layout",
        version="v1",
        map_name="warehouse_small",
        map_version="2026.1",
        agent_count=3,
        obstacle_count=8,
        shelf_count=24,
        delivery_zone_count=2,
        config_json={
            "grid_size": {"x": 24, "z": 16},
            "reward_profile": "baseline",
            "observation_type": "vector",
            "notes": "Seed configuration for Phase 3E verification.",
        },
    )

    db.add(environment_config)
    db.flush()

    simulation_run = SimulationRun(
        environment_config_id=environment_config.id,
        run_name="seed-simulation-run",
        environment_name="WarehouseSimulator-Seed",
        agent_count=3,
        map_version="2026.1",
        status=SimulationStatus.COMPLETED,
        started_at=now - timedelta(minutes=45),
        ended_at=now - timedelta(minutes=5),
        config_json={
            "mode": "seed",
            "unity_scene": "WarehouseSmall",
            "traffic_density": "low",
        },
    )

    db.add(simulation_run)
    db.flush()

    training_session = TrainingSession(
        simulation_run_id=simulation_run.id,
        environment_config_id=environment_config.id,
        algorithm="ppo",
        max_steps=500_000,
        current_step=150_000,
        learning_rate=0.0003,
        batch_size=1024,
        buffer_size=10240,
        checkpoint_interval=50_000,
        status=TrainingStatus.COMPLETED,
        started_at=now - timedelta(minutes=45),
        ended_at=now - timedelta(minutes=5),
    )

    db.add(training_session)
    db.flush()

    agents: list[Agent] = []

    for index in range(3):
        agent = Agent(
            simulation_run_id=simulation_run.id,
            agent_name=f"robot_{index + 1:02d}",
            agent_type="warehouse_robot",
            policy_name="ppo_seed_policy",
            spawn_position_x=float(index * 2),
            spawn_position_z=0.0,
            status=AgentStatus.ACTIVE,
            metadata_json={
                "battery_level": 95 - (index * 5),
                "max_speed": 2.5,
                "sensor_profile": "vector",
            },
        )
        db.add(agent)
        agents.append(agent)

    db.flush()

    episodes: list[Episode] = []

    for episode_number in range(1, 6):
        success = episode_number != 3
        episode = Episode(
            simulation_run_id=simulation_run.id,
            training_session_id=training_session.id,
            episode_number=episode_number,
            reward_total=18.5 + episode_number * 2.4 if success else 7.5,
            step_count=220 + episode_number * 15,
            success=success,
            collision_count=0 if success else 2,
            delivery_count=1 if success else 0,
            duration_seconds=38.0 + episode_number * 3.2,
            started_at=now - timedelta(minutes=40) + timedelta(minutes=episode_number * 5),
            ended_at=now - timedelta(minutes=39) + timedelta(minutes=episode_number * 5),
            metadata_json={
                "curriculum_level": "baseline",
                "episode_source": "seed",
            },
        )
        db.add(episode)
        episodes.append(episode)

    db.flush()

    agent_events: list[AgentEvent] = []

    event_types = [
        AgentEventType.SPAWNED,
        AgentEventType.MOVED,
        AgentEventType.PICKUP_STARTED,
        AgentEventType.PICKUP_COMPLETED,
        AgentEventType.DELIVERY_STARTED,
        AgentEventType.DELIVERY_COMPLETED,
        AgentEventType.REROUTE,
        AgentEventType.COLLISION_WARNING,
        AgentEventType.IDLE,
        AgentEventType.MOVED,
    ]

    for event_index in range(50):
        agent = agents[event_index % len(agents)]
        episode = episodes[event_index % len(episodes)]
        event_type = event_types[event_index % len(event_types)]

        event = AgentEvent(
            simulation_run_id=simulation_run.id,
            episode_id=episode.id,
            agent_id=agent.id,
            timestamp=now - timedelta(minutes=35) + timedelta(seconds=event_index * 12),
            step=event_index * 25,
            position_x=float((event_index % 12) + (event_index % 3) * 0.25),
            position_z=float((event_index % 8) + (event_index % 2) * 0.5),
            velocity=1.0 + (event_index % 5) * 0.15,
            action="move_to_target" if event_type == AgentEventType.MOVED else event_type.value,
            reward_delta=0.05 if event_type == AgentEventType.MOVED else 1.0,
            event_type=event_type,
            reason_code="normal_operation"
            if event_type != AgentEventType.REROUTE
            else "blocked_path",
            metadata_json={
                "source": "seed",
                "risk_score": round((event_index % 10) / 10, 2),
            },
        )
        db.add(event)
        agent_events.append(event)

    db.flush()

    for index in range(3):
        collision = Collision(
            simulation_run_id=simulation_run.id,
            episode_id=episodes[index + 1].id,
            agent_id=agents[index % len(agents)].id,
            other_agent_id=agents[(index + 1) % len(agents)].id if index == 1 else None,
            collision_type=CollisionType.AGENT if index == 1 else CollisionType.OBSTACLE,
            position_x=5.0 + index,
            position_z=3.0 + index * 0.5,
            impact_force=0.8 + index * 0.25,
            timestamp=now - timedelta(minutes=25) + timedelta(minutes=index * 3),
            metadata_json={
                "source": "seed",
                "severity": "low" if index != 2 else "medium",
            },
        )
        db.add(collision)

    for index in range(5):
        delivery = Delivery(
            simulation_run_id=simulation_run.id,
            episode_id=episodes[index].id,
            agent_id=agents[index % len(agents)].id,
            pickup_location=f"shelf_{index + 1:02d}",
            delivery_location="delivery_zone_a" if index % 2 == 0 else "delivery_zone_b",
            started_at=now - timedelta(minutes=30) + timedelta(minutes=index * 4),
            completed_at=now - timedelta(minutes=29) + timedelta(minutes=index * 4),
            duration_seconds=42.5 + index * 2.1,
            success=index != 2,
            reward=20.0 if index != 2 else 5.0,
            metadata_json={
                "source": "seed",
                "package_type": "standard",
            },
        )
        db.add(delivery)

    checkpoints: list[Checkpoint] = []

    for index, step in enumerate([50_000, 100_000, 150_000], start=1):
        checkpoint = Checkpoint(
            training_session_id=training_session.id,
            step=step,
            reward_mean=12.5 + index * 4.2,
            success_rate=0.62 + index * 0.08,
            collision_rate=0.20 - index * 0.03,
            file_path=f"models/seed/checkpoint_{step}.pt",
            storage_backend="minio",
            is_best=step == 150_000,
            metadata_json={
                "source": "seed",
                "trainer": "ppo",
            },
        )
        db.add(checkpoint)
        checkpoints.append(checkpoint)

    db.flush()

    model_v1 = ModelVersion(
        training_session_id=training_session.id,
        checkpoint_id=checkpoints[1].id,
        model_name="warehouse-ppo-policy",
        version="v0.1-seed",
        algorithm="ppo",
        file_path="models/seed/warehouse-ppo-policy-v0.1.pt",
        onnx_path="models/seed/warehouse-ppo-policy-v0.1.onnx",
        reward_mean=17.8,
        success_rate=0.76,
        collision_rate=0.14,
        is_active=False,
        metadata_json={"source": "seed"},
    )

    model_v2 = ModelVersion(
        training_session_id=training_session.id,
        checkpoint_id=checkpoints[2].id,
        model_name="warehouse-ppo-policy",
        version="v0.2-seed",
        algorithm="ppo",
        file_path="models/seed/warehouse-ppo-policy-v0.2.pt",
        onnx_path="models/seed/warehouse-ppo-policy-v0.2.onnx",
        reward_mean=21.2,
        success_rate=0.86,
        collision_rate=0.11,
        is_active=True,
        metadata_json={"source": "seed", "selected_for_demo": True},
    )

    db.add_all([model_v1, model_v2])

    for index, event in enumerate(agent_events[:3], start=1):
        explanation = LLMExplanation(
            agent_event_id=event.id,
            question=f"Why did robot behavior event {index} happen?",
            answer=(
                "The robot selected this action based on its current target, "
                "nearby obstacles, and reward optimization signals."
            ),
            model_name="gpt-seed-explainer",
            prompt_version="v1",
            latency_ms=180 + index * 25,
            metadata_json={
                "source": "seed",
                "context_window_seconds": 30,
            },
        )
        db.add(explanation)

    metric_names = [
        "average_reward",
        "success_rate",
        "collision_rate",
        "delivery_time",
        "steps_per_second",
    ]

    for index in range(20):
        metric = SystemMetric(
            simulation_run_id=simulation_run.id,
            training_session_id=training_session.id,
            metric_name=metric_names[index % len(metric_names)],
            metric_value=round(10.0 + index * 0.75, 3),
            metric_unit="score" if index % len(metric_names) == 0 else None,
            source=MetricSource.TRAINING if index % 2 == 0 else MetricSource.UNITY,
            timestamp=now - timedelta(minutes=30) + timedelta(seconds=index * 45),
            metadata_json={
                "source": "seed",
                "window": "rolling",
            },
        )
        db.add(metric)

    db.commit()


def main() -> None:
    with SessionLocal() as db:
        clear_database(db)
        seed_database(db)

    print("Seed data inserted successfully.")
    print("Inserted baseline demo dataset:")
    print("- 1 environment config")
    print("- 1 simulation run")
    print("- 1 training session")
    print("- 3 agents")
    print("- 5 episodes")
    print("- 50 agent events")
    print("- 3 collisions")
    print("- 5 deliveries")
    print("- 3 checkpoints")
    print("- 2 model versions")
    print("- 3 LLM explanations")
    print("- 20 system metrics")


if __name__ == "__main__":
    main()
