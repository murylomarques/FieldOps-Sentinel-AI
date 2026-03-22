# Assumptions and Limitations

This repository prioritizes local executability and deterministic behavior.

## Assumptions
- Single-region PostgreSQL deployment for demo
- Dispatcher and manager roles can submit approvals
- Simulation is deterministic and uses current DB snapshot
- Scenario optimization is done per order decision context

## Current limitations
- No asynchronous worker queue yet
- No distributed rate limiting backend
- No Alembic migration history committed yet (schema created via SQLAlchemy `create_all`)
- No external telemetry stack wired (only local metrics endpoint and hooks)
- Replay does not include real external outcome telemetry; it reconstructs from stored internal events

## Why these choices
They keep the project runnable in a laptop/dev environment while preserving realistic architecture patterns and extension points.
