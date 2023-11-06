from flask import Flask, render_template, request, redirect
from logging.config import dictConfig
from scheduler import config, docker

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


def show_success(message, jobs):
    return render_template(
            'index.html',
            trigger=message,
            docker_jobs=jobs
    )


def show_error(message, jobs):
    return render_template(
        'index.html',
        error=message,
        docker_jobs=jobs
    )


@app.route(f'{webroot}/index.html', methods=['POST'])
@app.route(f'{webroot}/', methods=['POST'])
@app.route(webroot, methods=['POST'])
def post_trigger():
    jobname = request.form.get('triggerJobName')

    if jobname is None:
        message = 'No valid job was triggered'
        return show_error(message, jobs)

    job = next((i for i in jobs if i.name == jobname), None)
    if job.jobtype == "exec":
        result = docker.start_exec(job)
    elif job.jobtype == "run":
        result = docker.start_run(job)

    if result:
        message = f'Job "{jobname}" was successfully triggered'
        return show_success(message, jobs)
    else:
        message = f'Job "{jobname}" could not be triggered'
        return show_error(message, jobs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
