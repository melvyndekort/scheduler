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

- `APPRISE_URL`: URL to your Apprise server (e.g., `https://apprise.mdekort.nl`)
- `APPRISE_TAG`: Tag for notifications (optional, defaults to `homelab`)
- `APPRISE_KEY`: Configuration key for stateful notifications (optional, defaults to `apprise`)
