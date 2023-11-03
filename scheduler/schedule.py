import schedule
import time
import logging

from croniter import croniter
from datetime import datetime

logger = logging.getLogger(__name__)


def get_next(job):
    base = datetime.now()
    iter = croniter(job.schedule, base)
    iter.get_next()

def job():
    logger.info('I was scheduled')

schedule.every(10).seconds.do(job)

def start():
    logger.info('Loop starting')
    while True:
        schedule.run_pending()
        time.sleep(1)
    logger.info('Loop finished')
