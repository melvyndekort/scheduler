from flask import Flask, render_template, request, redirect
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

from scheduler import config, docker
webroot = config.get_webroot()
jobs = config.get_jobs()


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
    if job.jobtype == "exec":
        result = docker.start_exec(job)
    elif job.jobtype == "run":
        result = docker.start_run(job)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
