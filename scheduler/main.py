"""Entry point: schedules jobs from config.yml and keeps them in sync."""
import logging
import os

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

import docker as docker_sdk
from scheduler import config, docker, notify

FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

CONFIG_RELOAD_INTERVAL = int(os.environ.get('CONFIG_RELOAD_INTERVAL', '10'))
RELOAD_JOB_ID = '__config_reload__'
# Default executor only has 10 threads, and each 'run' job holds one for its
# entire container lifetime. Give some headroom over the job count so a busy
# day of overlapping backups/syncs can't silently starve other jobs.
MAX_WORKERS = int(os.environ.get('MAX_WORKERS', '20'))

jobs = config.get_jobs()
scheduler = BlockingScheduler(executors={'default': ThreadPoolExecutor(MAX_WORKERS)})


def _on_job_event(event):
    """Alert when a job misses its scheduled run or raises unexpectedly.

    run_job() already logs/notifies its own docker-related failures; this
    is the backstop for anything that gets past that (executor exhaustion,
    a bug, an exception type run_job doesn't catch).
    """
    if event.code == EVENT_JOB_MISSED:
        notify.notify(f'Job {event.job_id} missed its scheduled run')
    else:
        notify.notify(f'Job {event.job_id} raised an unhandled error: {event.exception}')


def run_job(job):
    """Trigger a single job's docker action, logging (not raising) on failure."""
    logger.info('Triggering job %s', job.name)
    try:
        if job.jobtype == 'exec':
            docker.start_exec(job)
        elif job.jobtype == 'run':
            docker.start_run(job)
    except (docker_sdk.errors.DockerException, OSError, KeyError, ValueError) as e:
        logger.error(
            'An exception occured while triggering %s: %s',
            job.name,
            str(e)
        )


def _add_job(job):
    if job.name == RELOAD_JOB_ID:
        raise ValueError(
            f'Job name "{RELOAD_JOB_ID}" is reserved for the internal config-reload poller'
        )
    scheduler.add_job(
        func=run_job,
        trigger=CronTrigger.from_crontab(job.schedule),
        id=job.name,
        name=job.name,
        args=[job]
    )


def sync_jobs():
    """Reload config.yml and reconcile the scheduler with any changes.

    Only jobs that were added, removed, or actually changed are touched;
    unaffected jobs keep their existing schedule untouched.
    """
    new_jobs = config.reload()
    if new_jobs is None:
        return  # invalid config; already logged, keep running as-is

    old_by_name = {job.name: job for job in jobs}
    new_by_name = {job.name: job for job in new_jobs}

    for name in old_by_name.keys() - new_by_name.keys():
        logger.info('Removing job %s', name)
        scheduler.remove_job(name)

    for name, job in new_by_name.items():
        if old_by_name.get(name) != job:
            action = 'Rescheduling' if name in old_by_name else 'Adding'
            logger.info('%s job %s', action, name)
            if name in old_by_name:
                scheduler.remove_job(name)
            _add_job(job)
        # else: unchanged, leave its existing schedule untouched

    jobs[:] = new_jobs


def main():
    """Schedule all configured jobs plus the config-reload poller, then run."""
    for job in jobs:
        _add_job(job)

    scheduler.add_job(
        func=sync_jobs,
        trigger='interval',
        seconds=CONFIG_RELOAD_INTERVAL,
        id=RELOAD_JOB_ID,
        name=RELOAD_JOB_ID
    )
    scheduler.add_listener(_on_job_event, EVENT_JOB_MISSED | EVENT_JOB_ERROR)

    logger.info('Starting scheduler')
    scheduler.start()


if __name__ == "__main__":
    main()
