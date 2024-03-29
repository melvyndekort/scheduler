import pytest
import os

from scheduler.job import Job


def test_main_add_job(monkeypatch, config):
    from scheduler import main

    called = False
    def mock_start():
        nonlocal called
        called = True

    monkeypatch.setattr(main.scheduler, 'start', mock_start)

    main.main()
    jobs = main.scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == 'foobar'
    assert called

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
    main.run_job(job)


def test_run_job_failure(monkeypatch, config):
    from scheduler import main

    class mock_docker:
        def start_run(job):
            raise Exception()

    class mock_logger:
        def info(self, message, *args):
            pass

        def error(self, message, *args):
            assert 'foobar' in args

    monkeypatch.setattr(main, 'docker', mock_docker())
    monkeypatch.setattr(main, 'logger', mock_logger())

    job = Job(
        name='foobar',
        jobtype='run',
        schedule='foobar'
    )
    main.run_job(job)
