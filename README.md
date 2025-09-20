# SCHEDULER

## Badges

### Quality

[![Maintainability](https://api.codeclimate.com/v1/badges/473d8f4971a5c5968299/maintainability)](https://codeclimate.com/github/melvyndekort/scheduler/maintainability)
[![codecov](https://codecov.io/gh/melvyndekort/scheduler/graph/badge.svg?token=xtrnsfKuqV)](https://codecov.io/gh/melvyndekort/scheduler)

### Workflows

![pipeline](https://github.com/melvyndekort/scheduler/actions/workflows/pipeline.yml/badge.svg)

## Purpose

Run scheduled jobs in Docker and trigger them manually via a web interface

## Environment variables

The minimal environment variables are:

- `NTFY_URL`: URL to your ntfy topic (e.g., `https://your-ntfy-server.com/your-topic`)
- `NTFY_TOKEN`: Authentication token for your ntfy server
