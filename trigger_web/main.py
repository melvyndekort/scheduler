import logging

from flask import Flask, render_template, request
from trigger_scheduler import main as scheduler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index_get():
    jobs = scheduler.get_jobs()
    return render_template('index.html', jobs=jobs)

@app.route('/', methods=['POST'])
def index_post():
    name = request.args.get('name', None)
    if name is None:
        error = 'no name given'
        return render_template('index.html', error=error)
    else:
        return render_template('index.html', name=name)
