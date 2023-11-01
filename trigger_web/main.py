import logging
import os

from flask import Flask, render_template, request, redirect
from logging.config import dictConfig

from trigger_scheduler import main as scheduler
from trigger_docker import main as docker

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

app = Flask(__name__)

if 'WEBROOT' in os.environ:
    webroot = os.environ['WEBROOT']
else:
    webroot = '/scheduler'


@app.route('/')
def root_get():
    return redirect(webroot, code=302)

def get_jobs():
    jobs = scheduler.get_docker_jobs()
    containers = docker.get_triggered_containers()

    for container in containers:
        job = next((i for i in jobs if i.name == container['job']), None)
        job.addContainer(container)

    return jobs

@app.route(webroot, methods=['GET'])
def index_get():
    return render_template(
        'index.html',
        webroot=webroot,
        docker_jobs=get_jobs()
    )

@app.route(webroot, methods=['POST'])
def index_post():
    jobname = request.form.get('triggerJobName')

    if jobname is None:
        return render_template(
            'index.html',
            webroot=webroot,
            error='No valid job was triggered',
            docker_jobs=get_jobs()
        )

    result = docker.run_job(jobname)

    if result:
        return render_template(
            'index.html',
            webroot=webroot,
            trigger=f'Job "{jobname}" was successfully triggered',
            docker_jobs=get_jobs()
        )
    else:
        return render_template(
            'index.html',
            webroot=webroot,
            error=f'Job "{jobname}" could not be triggered',
            docker_jobs=get_jobs()
        )
