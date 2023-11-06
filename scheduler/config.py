import os
import logging
from pathlib import Path
import yaml
from scheduler.job import Job

logger = logging.getLogger(__name__)

if 'CONFIG' in os.environ:
    config = os.environ['CONFIG']
else:
    config = '/config/config.yml'
if not Path(config).is_file():
    raise Exception('No valid config file found')

with open(config, 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        logger.error(e)
        raise

def get_webroot():
    if 'WEBROOT' in os.environ:
        webroot = os.environ['WEBROOT']
    elif data.get('webroot'):
        webroot = data['webroot']
    else:
        logger.warning('Using default webroot "/scheduler"')
        webroot = '/scheduler'
    return webroot

def get_jobs():
    jobs = []
    for elem in data['jobs']:
        job = Job(**elem)
        jobs.append(job)
    return jobs
