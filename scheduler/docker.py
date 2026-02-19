import os
import logging
from cachetools.func import ttl_cache
import docker
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


def execute(job):
    if job.jobtype == "exec":
        return start_exec(job)
    elif job.jobtype == "run":
        return start_run(job)


def start_exec(job):
    logger.info(
        'Executing command in running container %s: %s',
        job.container,
        job.command
    )
    try:
        container = client.containers.get(job.container)
        container.exec_run(
            job.command,
            user=job.user,
            detach=True,
            stream=True
        )
        return True
    except Exception as e:
        message = f'Executing command in {job.container} failed: {str(e)}'
        logger.error(message)
        notify.notify(message)
        raise


def replace_environment(envlist):
    copy = []
    for env in envlist:
        if '${' in env:
            envname = env[env.find('${')+2: env.find('}')]
            item = env.replace('${' + envname + '}', os.environ[envname])
            copy.append(item)
        else:
            copy.append(env)

    return copy


def start_run(job):
    logger.info('Running container %s', job.name)
    try:
        container = client.containers.run(
            image=job.image,
            command=job.command,
            name=job.name,
            detach=True,
            auto_remove=not job.keep_containers,
            environment=replace_environment(job.environment),
            network=job.network,
            remove=not job.keep_containers,
            volumes=job.volumes
        )
        return container.short_id
    except Exception as e:
        message = f'Running container {job.name} failed: {str(e)}'
        logger.error(message)
        notify.notify(message)
        raise
