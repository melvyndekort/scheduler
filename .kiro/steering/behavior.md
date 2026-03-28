# scheduler

> For global standards, way-of-workings, and pre-commit checklist, see `~/.kiro/steering/behavior.md`

## Role

Python developer and DevOps engineer.

## What This Does

Scheduled job runner with a Flask web UI for manual triggering. Uses APScheduler for scheduling and Docker SDK for container operations. Runs on homelab as a Docker container.

## Repository Structure

- `scheduler/` — Application source (Flask app + APScheduler + Docker SDK)
- `tests/` — Test suite
- `docker/` — `supervisord.conf` and `config.yml` for container runtime
- `Dockerfile` — Multi-stage build, runs supervisord (scheduler + gunicorn)
- `Makefile` — `install`, `test`, `lint` (pylint), `build`, `full-build`, `dev`, `run`, `scheduler`

## Deployment

- Container image: `ghcr.io/melvyndekort/scheduler:latest`
- Runs on homelab Docker via Portainer

## Related Repositories

- `~/src/melvyndekort/homelab` — Docker Compose stack that runs this container
