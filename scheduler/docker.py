import logging
import docker

from cachetools.func import ttl_cache

logger = logging.getLogger()

client = docker.from_env()


def get_running_by_job(jobname):
    return [{'name': c.name, 'id': c.short_id} for c in get_all_containers() if c.labels.get('trigger-job') == jobname]

def get_running_by_name(name):
    try:
        c = client.containers.get(name)
        return {'name': c.name, 'id': c.short_id}
    except docker.errors.NotFound:
        return False

@ttl_cache(maxsize=128, ttl=1)
def get_all_containers():
    logger.info('Retrieving running docker containers')
    return client.containers.list()

def run_job(job):
    if job.jobtype == 'run':
        container = client.containers.run(
            image=job.image,
            command=job.command,
            detach=True,
            auto_remove=True,
            environment=job.environment,
            labels={'trigger-job': job.name},
            network=job.network,
            remove=True,
            volumes=job.volumes
        )
        return container.short_id
    elif job.jobtype == 'exec':
        logger.info(f'Executing command in running container {job.container}:\n{job.command}')
        container = client.containers.get(job.container)
        exec_id = client.api.exec_create(
            container=container.id,
            cmd=job.command,
            user=job.user
        )
        client.api.exec_start(
            exec_id=exec_id,
            detach=True
        )
        return True
