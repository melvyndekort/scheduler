"""Docker container management for scheduled jobs."""
import os
import logging
from cachetools.func import ttl_cache
import docker
from scheduler import notify

logger = logging.getLogger(__name__)

CLIENT = None


def get_client():
    """Lazy-load Docker client to avoid fork issues with gunicorn."""
    global CLIENT  # pylint: disable=global-statement
    if CLIENT is None:
        CLIENT = docker.from_env()
    return CLIENT


@ttl_cache(maxsize=128, ttl=1)
def is_running(name):
    """Check if a container is currently running."""
    try:
        container = get_client().containers.get(name)
        return container.status == 'running'
    except docker.errors.NotFound:
        return False


def execute(job):
    """Execute a job based on its type."""
    if job.jobtype == "exec":
        return start_exec(job)
    if job.jobtype == "run":
        return start_run(job)
    return None


def start_exec(job):
    """Execute a command in an existing running container."""
    logger.info(
        'Executing command in running container %s: %s',
        job.container,
        job.command
    )
    try:
        container = get_client().containers.get(job.container)
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
    """Replace environment variable placeholders with actual values."""
    copy = []
    for env in envlist:
        if '${' in env:
            envname = env[env.find('${')+2: env.find('}')]
            item = env.replace('${' + envname + '}', os.environ[envname])
            copy.append(item)
        else:
            copy.append(env)

    return copy


def load_env_file(env_file_paths):
    """Load environment variables from env files.

    Supports:
    - Comments (lines starting with #)
    - Empty lines
    - Quoted values (single and double quotes)
    - Special characters and non-ASCII
    """
    env_dict = {}
    for env_file_path in env_file_paths:
        try:
            with open(env_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if value and value[0] in ('"', "'") and value[-1] == value[0]:
                            value = value[1:-1]

                        env_dict[key] = value
        except FileNotFoundError:
            logger.warning('Env file not found: %s', env_file_path)
    return env_dict


def start_run(job):
    """Start a new container and wait for completion, removing only on success."""
    logger.info('Running container %s', job.name)
    try:
        # Remove existing container if it exists (stopped or exited)
        try:
            old_container = get_client().containers.get(job.name)
            if old_container.status != 'running':
                logger.info('Removing existing stopped container %s', job.name)
                old_container.remove()
        except docker.errors.NotFound:
            pass  # Container doesn't exist, that's fine

        # Merge environment from env_file and environment list
        env_dict = load_env_file(job.env_file) if job.env_file else {}
        env_list = replace_environment(job.environment)

        # Convert list to dict and merge
        for env in env_list:
            if '=' in env:
                key, value = env.split('=', 1)
                env_dict[key] = value

        container = get_client().containers.run(
            image=job.image,
            command=job.command,
            name=job.name,
            detach=True,
            auto_remove=False,
            environment=env_dict,
            network=job.network,
            volumes=job.volumes
        )

        # Wait for container and check exit code
        result = container.wait()
        exit_code = result['StatusCode']

        if exit_code == 0:
            logger.info('Container %s completed successfully, removing', job.name)
            container.remove()
        else:
            logger.error(
                'Container %s failed with exit code %s, keeping for inspection',
                job.name, exit_code
            )
            notify.notify(f'Container {job.name} failed with exit code {exit_code}')

        return container.short_id
    except Exception as exc:
        message = f'Running container {job.name} failed: {str(exc)}'
        logger.error(message)
        notify.notify(message)
        raise
