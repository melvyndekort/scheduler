import sched
import yaml
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    pass

def get_jobs():
    with open('jobs.yml', 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logger.error(e)

    return data
