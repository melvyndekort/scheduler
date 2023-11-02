import logging
import docker

from cachetools.func import ttl_cache

logger = logging.getLogger()

client = docker.from_env()

@ttl_cache(maxsize=128, ttl=1)
def is_running(name):
    try:
        client.containers.get(name)
        return True
    except docker.errors.NotFound:
        return False

def start_exec(job):
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

def start_run(job):
    container = client.containers.run(
        image=job.image,
        command=job.command,
        name=job.name,
        detach=True,
        auto_remove=True,
        environment=job.environment,
        network=job.network,
        remove=True,
        volumes=job.volumes
    )
    return container.short_id
