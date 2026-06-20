# Deployment Guide

This document will describe how to deploy the system locally, on a VPS, and in a production-like environment.

## Planned Deployment Targets

- Local Docker Compose
- Cloud GPU training instance
- VPS-based backend and dashboard deployment
- Production Docker Compose
- Optional managed PostgreSQL
- Optional object storage provider

## Deployment Goals

- One-command local startup
- Environment-based configuration
- HTTPS-ready production deployment
- Persistent database and object storage volumes
- Health checks for all services
- Clear rollback strategy
