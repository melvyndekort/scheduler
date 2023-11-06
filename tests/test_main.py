import pytest
import os

from scheduler.job import Job


@pytest.fixture
def config(tmpdir):
    config = f'{tmpdir}/config.yml'
    with open(config, "w") as file:
        file.write('''
jobs:
  - name: 'foobar'
    jobtype: 'run'
    schedule: '* * * * *'
''')
    os.environ['CONFIG'] = config

def test_main(monkeypatch, config):
    from scheduler import main

    class mock_scheduler:
        def add_job(self, **kwargs):
            assert kwargs['id'] == 'foobar'

        def start(self):
            pass

    monkeypatch.setattr(main, 'jobs', [])
    monkeypatch.setattr(main, 'scheduler', mock_scheduler())

    main.main()

def test_main_add_job(monkeypatch, config):
    from scheduler import main

    def mock_start():
        pass

    monkeypatch.setattr(main.scheduler, 'start', mock_start)

    main.main()
    jobs = main.scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == 'foobar'

def test_run_job_success(monkeypatch, config):
    from scheduler import main

    class mock_docker:
        def start_run(job):
            assert job.name == 'foobar'

    monkeypatch.setattr(main, 'docker', mock_docker())

    job = Job(
        name='foobar',
        jobtype='run',
        schedule='foobar'
    )
    main.run_job(job);


def test_run_job_failure(monkeypatch, config):
    from scheduler import main

    class mock_docker:
        def start_run(job):
            raise Exception()

    class mock_logger:
        def info(self, message):
            pass

        def error(self, message):
            assert 'foobar' in message

    monkeypatch.setattr(main, 'docker', mock_docker())
    monkeypatch.setattr(main, 'logger', mock_logger())

    job = Job(
        name='foobar',
        jobtype='run',
        schedule='foobar'
    )
    main.run_job(job);
