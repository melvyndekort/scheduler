"""Loads and hot-reloads job definitions from config.yml."""
import os
import logging
from pathlib import Path
import yaml
from scheduler.job import Job

logger = logging.getLogger(__name__)

if 'CONFIG' in os.environ:
    CONFIG_PATH = os.environ['CONFIG']
else:
    CONFIG_PATH = '/config/config.yml'
if not Path(CONFIG_PATH).is_file():
    raise FileNotFoundError(f'No valid config file found: {CONFIG_PATH}')

with open(CONFIG_PATH, 'r', encoding='utf-8') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        logger.error(e)
        raise


def get_webroot():
    """Return the configured webroot, preferring the WEBROOT env var."""
    if 'WEBROOT' in os.environ:
        webroot = os.environ['WEBROOT']
    elif data.get('webroot'):
        webroot = data['webroot']
    else:
        logger.warning('Using default webroot "/scheduler"')
        webroot = '/scheduler'
    return webroot


def get_jobs():
    """Build the current list of Job objects from the loaded config."""
    jobs = []
    for elem in data['jobs']:
        job = Job(**elem)
        jobs.append(job)
    return jobs


def reload():
    """Re-read the config file from disk.

    Returns the new job list on success. On invalid YAML or a malformed job
    definition, logs the error and returns None, leaving the last-known-good
    config in place.
    """
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
            new_data = yaml.safe_load(file)
        new_jobs = [Job(**elem) for elem in new_data['jobs']]
    except (yaml.YAMLError, TypeError, KeyError) as e:
        logger.error('Failed to reload %s, keeping last-known-good config: %s', CONFIG_PATH, e)
        return None
    data.clear()
    data.update(new_data)
    return new_jobs
