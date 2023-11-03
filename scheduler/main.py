import logging

FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

from scheduler import config, docker, schedule
jobs = config.get_jobs()


def main():
    schedule.start()

if __name__ == "__main__":
    main()
