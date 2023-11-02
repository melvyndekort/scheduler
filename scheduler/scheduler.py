import schedule
import croniter
import yaml
import logging

from scheduler.job import Job

logger = logging.getLogger()


def get_docker_jobs(config):
    docker_jobs = []

    with open(config, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logger.error(e)

    for elem in data['docker']:
        job = Job(
            name=elem.get('name'),
            jobtype=elem.get('type'),
            image=elem.get('image'),
            schedule=elem.get('schedule'),
            command=elem.get('command')
        )
        docker_jobs.append(job)

    return docker_jobs
