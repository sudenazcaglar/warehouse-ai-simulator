# Training Guide

This document will describe how reinforcement learning training is configured, executed, monitored, checkpointed, and resumed.

## Planned Training Workflow

```text
Unity Environment
    ↓
ML-Agents PPO Trainer
    ↓
TensorBoard Metrics
    ↓
Checkpoint Files
    ↓
Model Registry
```

## Planned Topics

- Unity ML-Agents setup
- Observation design
- Action space design
- Reward shaping
- PPO configuration
- Checkpointing
- Resume training
- ONNX export
- Cloud GPU training
