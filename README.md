# SCHEDULER

## Badges

### Quality

[![Maintainability](https://api.codeclimate.com/v1/badges/473d8f4971a5c5968299/maintainability)](https://codeclimate.com/github/melvyndekort/scheduler/maintainability)
[![codecov](https://codecov.io/gh/melvyndekort/scheduler/graph/badge.svg?token=xtrnsfKuqV)](https://codecov.io/gh/melvyndekort/scheduler)

### Workflows

![pipeline](https://github.com/melvyndekort/scheduler/actions/workflows/pipeline.yml/badge.svg)

## Purpose

Run scheduled jobs in Docker and trigger them manually via a web interface.
Job definitions are loaded from `config.yml` and hot-reloaded automatically -
editing the file takes effect without restarting the container, and only the
jobs that actually changed are affected.

## Environment variables

The minimal environment variables are:

- `APPRISE_URL`: URL to your Apprise server (e.g., `https://apprise.mdekort.nl`)
- `APPRISE_TAG`: Tag for notifications (optional, defaults to `homelab`)
- `APPRISE_KEY`: Configuration key for stateful notifications (optional, defaults to `apprise`)

Optional tuning:

- `CONFIG`: path to the job definitions file (optional, defaults to `/config/config.yml`)
- `WEBROOT`: URL path prefix the web UI is served under (optional, falls back to a `webroot` key in `config.yml`, then to `/scheduler`)
- `CONFIG_RELOAD_INTERVAL`: seconds between checks for `config.yml` changes (optional, defaults to `10`)
- `MAX_WORKERS`: max number of jobs that can run concurrently (optional, defaults to `20`)
