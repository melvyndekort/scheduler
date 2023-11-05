import logging
import docker
import os

from cachetools.func import ttl_cache
from scheduler import notify

logger = logging.getLogger(__name__)

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
    try:
        container = client.containers.get(job.container)
        container.exec_run(
            job.command,
            user=job.user,
            detach=True,
            stream=True
        )
        return True
    except:
        message = f'Executing command in {job.container} failed'
        logger.error(message)
        notify.notify(message)
        raise

def replace_environment(envlist):
    copy = []
    for env in envlist:
        if '${' in env:
            envname = env[env.find('${')+2 : env.find('}')]
            item = env.replace('${' + envname + '}', os.environ[envname])
            copy.append(item)
        else:
            copy.append(env)

    return copy

def start_run(job):
    logger.info(f'Running container {job.name}')
    try:
        container = client.containers.run(
            image=job.image,
            command=job.command,
            name=job.name,
            detach=True,
            auto_remove=True,
            environment=replace_environment(job.environment),
            network=job.network,
            remove=True,
            volumes=job.volumes
        )
        return container.short_id
    except:
        message = f'Running container {job.name} failed'
        logger.error(message)
        notify.notify(message)
        raise
