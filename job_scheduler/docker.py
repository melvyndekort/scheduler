import logging
import docker

logger = logging.getLogger()

client = docker.from_env()


def get_triggered_containers():
    triggered = []

    for container in client.containers.list():
        if 'trigger-job' in container.labels:
            triggered.append({
                'name': container.name,
                'id': container.short_id,
                'job': container.labels['trigger-job'],
            })

    return triggered

def run_job(jobname):
    container_id = 123456

    return container_id
