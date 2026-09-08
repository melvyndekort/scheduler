import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from scheduler import config, docker

FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

CONFIG_RELOAD_INTERVAL = int(os.environ.get('CONFIG_RELOAD_INTERVAL', '10'))

jobs = config.get_jobs()
scheduler = BlockingScheduler()


def run_job(job):
    logger.info('Triggering job %s', job.name)
    try:
        if job.jobtype == 'exec':
            docker.start_exec(job)
        elif job.jobtype == 'run':
            docker.start_run(job)
    except Exception as e:
        logger.error(
            'An exception occured while triggering %s: %s',
            job.name,
            str(e)
        )


def _add_job(job):
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
    for job in jobs:
        _add_job(job)

    scheduler.add_job(
        func=sync_jobs,
        trigger='interval',
        seconds=CONFIG_RELOAD_INTERVAL,
        id='__config_reload__',
        name='__config_reload__'
    )

    logger.info('Starting scheduler')
    scheduler.start()


if __name__ == "__main__":
    main()
