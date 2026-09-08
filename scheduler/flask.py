"""Flask UI for viewing and manually triggering scheduled jobs."""
from logging.config import dictConfig

from flask import Flask, render_template, request, redirect
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


def current_jobs():
    """Reload config.yml and return the current job list.

    On invalid YAML, logs the error and returns the last-known-good jobs.
    """
    config.reload()
    return config.get_jobs()


@app.route('/')
def root_get():
    """Redirect the bare root path to the configured webroot."""
    return redirect(webroot, code=302)


@app.route('/health')
def health():
    """Liveness/readiness probe endpoint."""
    return {'status': 'ok'}, 200


@app.route(f'{webroot}/index.html', methods=['GET'])
@app.route(f'{webroot}/', methods=['GET'])
@app.route(webroot, methods=['GET'])
def index_get():
    """Render the job table."""
    return render_template(
        'index.html',
        docker_jobs=current_jobs()
    )


def show_success(message, jobs):
    """Render the job table with a success banner."""
    return render_template(
            'index.html',
            trigger=message,
            docker_jobs=jobs
    )


def show_error(message, jobs):
    """Render the job table with an error banner."""
    return render_template(
        'index.html',
        error=message,
        docker_jobs=jobs
    )


@app.route(f'{webroot}/index.html', methods=['POST'])
@app.route(f'{webroot}/', methods=['POST'])
@app.route(webroot, methods=['POST'])
def post_trigger():
    """Handle a manual job trigger from the web UI."""
    jobs = current_jobs()
    jobname = request.form.get('triggerJobName')

    if not jobname:
        return show_error('No valid job was triggered', jobs)

    job = next((i for i in jobs if i.name == jobname), None)
    result = docker.execute(job)

    if result:
        message = f'Job "{jobname}" was successfully triggered'
        return show_success(message, jobs)

    message = f'Job "{jobname}" could not be triggered'
    return show_error(message, jobs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
