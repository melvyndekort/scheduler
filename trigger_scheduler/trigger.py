import yaml
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_jobs():
    with open('jobs.yml', 'r') as stream:
        try:
            d = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logger.error(e)

    return d

if __name__ == '__main__':
    jobs = get_jobs()
    logger.info(jobs)
