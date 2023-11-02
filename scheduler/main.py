import logging
import os
import yaml

from pathlib import Path
from flask import Flask, render_template, request, redirect
from logging.config import dictConfig

from scheduler import docker
from scheduler.job import Job

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

if 'CONFIG' in os.environ:
    config = os.environ['CONFIG']
else:
    config = 'config.yml'
if not Path(config).is_file():
    raise Exception('Config is not a valid file')

jobs = []
with open(config, 'r') as stream:
    try:
        data = yaml.safe_load(stream)

        for elem in data['jobs']:
            job = Job(**elem)
            jobs.append(job)
    except yaml.YAMLError as e:
        app.logger.error(e)

app = Flask(__name__)

if 'WEBROOT' in os.environ:
    webroot = os.environ['WEBROOT']
else:
    app.logger.warn('Using default webroot "/scheduler"')
    webroot = '/scheduler'


@app.route('/')
def root_get():
    return redirect(webroot, code=302)

@app.route(f'{webroot}/index.html', methods=['GET'])
@app.route(f'{webroot}/', methods=['GET'])
@app.route(webroot, methods=['GET'])
def index_get():
    return render_template(
        'index.html',
        docker_jobs=jobs
    )

@app.route(f'{webroot}/index.html', methods=['POST'])
@app.route(f'{webroot}/', methods=['POST'])
@app.route(webroot, methods=['POST'])
def post_trigger():
    jobname = request.form.get('triggerJobName')

    if jobname is None:
        return render_template(
            'index.html',
            error='No valid job was triggered',
            docker_jobs=jobs
        )

    job = next((i for i in jobs if i.name == jobname), None)
    result = docker.run_job(job)

    if result:
        return render_template(
            'index.html',
            trigger=f'Job "{jobname}" was successfully triggered',
            docker_jobs=jobs
        )
    else:
        return render_template(
            'index.html',
            error=f'Job "{jobname}" could not be triggered',
            docker_jobs=jobs
        )
