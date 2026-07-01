from datetime import datetime, timedelta, timezone
from random import Random
from uuid import uuid4

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


def generate_demo_data(db: Session) -> None:
    random = Random(42)
    now = datetime.now(timezone.utc)
    suffix = uuid4().hex[:8]

    environment_config = EnvironmentConfig(
        name=f"generated-warehouse-layout-{suffix}",
        version="v1",
        map_name="warehouse_generated",
        map_version="2026.generated",
        agent_count=5,
        obstacle_count=14,
        shelf_count=48,
        delivery_zone_count=4,
        config_json={
            "grid_size": {"x": 40, "z": 28},
            "reward_profile": "generated-demo",
            "traffic_density": "medium",
            "generator_seed": 42,
        },
    )

    db.add(environment_config)
    db.flush()

    simulation_run = SimulationRun(
        environment_config_id=environment_config.id,
        run_name=f"generated-demo-run-{suffix}",
        environment_name="WarehouseSimulator-Generated",
        agent_count=5,
        map_version="2026.generated",
        status=SimulationStatus.COMPLETED,
        started_at=now - timedelta(hours=2),
        ended_at=now - timedelta(minutes=10),
        config_json={
            "mode": "generated_demo",
            "unity_scene": "WarehouseGenerated",
            "generator_suffix": suffix,
        },
    )

    db.add(simulation_run)
    db.flush()

    training_session = TrainingSession(
        simulation_run_id=simulation_run.id,
        environment_config_id=environment_config.id,
        algorithm="ppo",
        max_steps=1_000_000,
        current_step=400_000,
        learning_rate=0.0003,
        batch_size=2048,
        buffer_size=20480,
        checkpoint_interval=100_000,
        status=TrainingStatus.COMPLETED,
        started_at=now - timedelta(hours=2),
        ended_at=now - timedelta(minutes=10),
    )

    db.add(training_session)
    db.flush()

    agents: list[Agent] = []

    for index in range(5):
        agent = Agent(
            simulation_run_id=simulation_run.id,
            agent_name=f"generated_robot_{index + 1:02d}_{suffix}",
            agent_type="warehouse_robot",
            policy_name="ppo_generated_policy",
            spawn_position_x=float(index * 3),
            spawn_position_z=float(index % 2),
            status=AgentStatus.ACTIVE,
            metadata_json={
                "battery_level": random.randint(70, 100),
                "max_speed": round(random.uniform(1.8, 3.0), 2),
                "source": "generated_demo",
            },
        )
        db.add(agent)
        agents.append(agent)

    db.flush()

    episodes: list[Episode] = []

    for episode_number in range(1, 11):
        collision_count = random.randint(0, 2)
        delivery_count = random.randint(1, 4)
        success = collision_count <= 1

        episode = Episode(
            simulation_run_id=simulation_run.id,
            training_session_id=training_session.id,
            episode_number=episode_number,
            reward_total=round(random.uniform(15.0, 45.0), 3),
            step_count=random.randint(180, 420),
            success=success,
            collision_count=collision_count,
            delivery_count=delivery_count,
            duration_seconds=round(random.uniform(30.0, 95.0), 3),
            started_at=now - timedelta(minutes=100) + timedelta(minutes=episode_number * 7),
            ended_at=now - timedelta(minutes=96) + timedelta(minutes=episode_number * 7),
            metadata_json={
                "source": "generated_demo",
                "traffic_density": "medium",
            },
        )
        db.add(episode)
        episodes.append(episode)

    db.flush()

    events: list[AgentEvent] = []
    event_types = list(AgentEventType)

    for event_index in range(200):
        agent = agents[event_index % len(agents)]
        episode = episodes[event_index % len(episodes)]
        event_type = event_types[event_index % len(event_types)]

        event = AgentEvent(
            simulation_run_id=simulation_run.id,
            episode_id=episode.id,
            agent_id=agent.id,
            timestamp=now - timedelta(minutes=95) + timedelta(seconds=event_index * 20),
            step=event_index * 10,
            position_x=round(random.uniform(0.0, 40.0), 3),
            position_z=round(random.uniform(0.0, 28.0), 3),
            velocity=round(random.uniform(0.0, 3.0), 3),
            action=f"generated_action_{event_type.value}",
            reward_delta=round(random.uniform(-0.5, 2.0), 3),
            event_type=event_type,
            reason_code=random.choice(
                [
                    "normal_operation",
                    "blocked_path",
                    "target_reached",
                    "traffic_avoidance",
                    "low_collision_risk",
                ]
            ),
            metadata_json={
                "source": "generated_demo",
                "collision_risk": round(random.uniform(0.0, 1.0), 3),
            },
        )
        db.add(event)
        events.append(event)

    db.flush()

    for index in range(8):
        collision = Collision(
            simulation_run_id=simulation_run.id,
            episode_id=episodes[index % len(episodes)].id,
            agent_id=agents[index % len(agents)].id,
            other_agent_id=agents[(index + 1) % len(agents)].id if index % 2 == 0 else None,
            collision_type=random.choice(list(CollisionType)),
            position_x=round(random.uniform(0.0, 40.0), 3),
            position_z=round(random.uniform(0.0, 28.0), 3),
            impact_force=round(random.uniform(0.1, 2.5), 3),
            timestamp=now - timedelta(minutes=80) + timedelta(minutes=index * 6),
            metadata_json={
                "source": "generated_demo",
                "severity": random.choice(["low", "medium"]),
            },
        )
        db.add(collision)

    for index in range(20):
        delivery = Delivery(
            simulation_run_id=simulation_run.id,
            episode_id=episodes[index % len(episodes)].id,
            agent_id=agents[index % len(agents)].id,
            pickup_location=f"generated_shelf_{index + 1:03d}",
            delivery_location=f"delivery_zone_{(index % 4) + 1}",
            started_at=now - timedelta(minutes=85) + timedelta(minutes=index * 3),
            completed_at=now - timedelta(minutes=84) + timedelta(minutes=index * 3),
            duration_seconds=round(random.uniform(25.0, 90.0), 3),
            success=random.random() > 0.1,
            reward=round(random.uniform(5.0, 25.0), 3),
            metadata_json={
                "source": "generated_demo",
                "priority": random.choice(["low", "normal", "high"]),
            },
        )
        db.add(delivery)

    checkpoints: list[Checkpoint] = []

    for step in [100_000, 200_000, 300_000, 400_000]:
        checkpoint = Checkpoint(
            training_session_id=training_session.id,
            step=step,
            reward_mean=round(random.uniform(15.0, 40.0), 3),
            success_rate=round(random.uniform(0.65, 0.92), 3),
            collision_rate=round(random.uniform(0.05, 0.25), 3),
            file_path=f"models/generated/{suffix}/checkpoint_{step}.pt",
            storage_backend="minio",
            is_best=step == 400_000,
            metadata_json={
                "source": "generated_demo",
                "suffix": suffix,
            },
        )
        db.add(checkpoint)
        checkpoints.append(checkpoint)

    db.flush()

    for index, checkpoint in enumerate(checkpoints[-2:], start=1):
        model_version = ModelVersion(
            training_session_id=training_session.id,
            checkpoint_id=checkpoint.id,
            model_name=f"warehouse-generated-policy-{suffix}",
            version=f"v{index}",
            algorithm="ppo",
            file_path=f"models/generated/{suffix}/policy_v{index}.pt",
            onnx_path=f"models/generated/{suffix}/policy_v{index}.onnx",
            reward_mean=checkpoint.reward_mean,
            success_rate=checkpoint.success_rate,
            collision_rate=checkpoint.collision_rate,
            is_active=index == 2,
            metadata_json={
                "source": "generated_demo",
                "suffix": suffix,
            },
        )
        db.add(model_version)

    for index, event in enumerate(events[:5], start=1):
        explanation = LLMExplanation(
            agent_event_id=event.id,
            question=f"What explains generated event {index}?",
            answer=(
                "The event was generated from synthetic robot telemetry and "
                "represents a plausible decision in a warehouse simulation."
            ),
            model_name="gpt-generated-explainer",
            prompt_version="v1",
            latency_ms=random.randint(120, 500),
            metadata_json={
                "source": "generated_demo",
                "suffix": suffix,
            },
        )
        db.add(explanation)

    metric_names = [
        "average_reward",
        "success_rate",
        "collision_rate",
        "average_delivery_time",
        "congestion_score",
        "steps_per_second",
    ]

    for index in range(50):
        metric = SystemMetric(
            simulation_run_id=simulation_run.id,
            training_session_id=training_session.id,
            metric_name=metric_names[index % len(metric_names)],
            metric_value=round(random.uniform(0.0, 100.0), 3),
            metric_unit=random.choice(["score", "percent", "seconds", None]),
            source=random.choice(list(MetricSource)),
            timestamp=now - timedelta(minutes=90) + timedelta(seconds=index * 60),
            metadata_json={
                "source": "generated_demo",
                "suffix": suffix,
            },
        )
        db.add(metric)

    db.commit()

    print("Synthetic demo data generated successfully.")
    print(f"Generated suffix: {suffix}")
    print("Inserted generated dataset:")
    print("- 1 environment config")
    print("- 1 simulation run")
    print("- 1 training session")
    print("- 5 agents")
    print("- 10 episodes")
    print("- 200 agent events")
    print("- 8 collisions")
    print("- 20 deliveries")
    print("- 4 checkpoints")
    print("- 2 model versions")
    print("- 5 LLM explanations")
    print("- 50 system metrics")


def main() -> None:
    with SessionLocal() as db:
        generate_demo_data(db)


if __name__ == "__main__":
    main()
