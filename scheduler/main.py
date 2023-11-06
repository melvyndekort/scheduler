import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from scheduler import config, docker

FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

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
        logger.error('An exception occured while triggering %s: %s', job.name, str(e))

def main():
    for job in jobs:
        scheduler.add_job(
            func=run_job,
            trigger=CronTrigger.from_crontab(job.schedule),
            id=job.name,
            name=job.name,
            args=[job]
        )

    logger.info('Starting scheduler')
    scheduler.start()


if __name__ == "__main__":
    main()
