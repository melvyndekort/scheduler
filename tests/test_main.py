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
    job_ids = {job.id for job in jobs}
    assert job_ids == {'foobar', '__config_reload__'}
    assert called

def test_run_job_success(monkeypatch, config):
    from scheduler import main

    class mock_docker:
        def start_run(job):
            assert job.name == 'foobar'

    monkeypatch.setattr(main, 'docker', mock_docker)

    job = Job(
        name='foobar',
        jobtype='run',
        schedule='foobar'
    )
    main.run_job(job)


def _fresh_scheduler(monkeypatch, main):
    from apscheduler.schedulers.blocking import BlockingScheduler

    fresh = BlockingScheduler()
    monkeypatch.setattr(main, 'scheduler', fresh)
    return fresh


def test_sync_jobs_adds_new_job(monkeypatch, config):
    from scheduler import main

    scheduler = _fresh_scheduler(monkeypatch, main)
    monkeypatch.setattr(main, 'jobs', [])
    new_job = Job(name='foobar', jobtype='run', schedule='* * * * *')
    monkeypatch.setattr(main.config, 'reload', lambda: [new_job])

    main.sync_jobs()

    assert {job.id for job in scheduler.get_jobs()} == {'foobar'}
    assert main.jobs == [new_job]


def test_sync_jobs_removes_missing_job(monkeypatch, config):
    from scheduler import main

    scheduler = _fresh_scheduler(monkeypatch, main)
    old_job = Job(name='foobar', jobtype='run', schedule='* * * * *')
    main._add_job(old_job)
    monkeypatch.setattr(main, 'jobs', [old_job])
    monkeypatch.setattr(main.config, 'reload', lambda: [])

    main.sync_jobs()

    assert scheduler.get_jobs() == []
    assert main.jobs == []


def test_sync_jobs_reschedules_changed_job(monkeypatch, config):
    from apscheduler.triggers.cron import CronTrigger
    from scheduler import main

    scheduler = _fresh_scheduler(monkeypatch, main)
    old_job = Job(name='foobar', jobtype='run', schedule='* * * * *')
    main._add_job(old_job)
    monkeypatch.setattr(main, 'jobs', [old_job])
    new_job = Job(name='foobar', jobtype='run', schedule='0 0 * * *')
    monkeypatch.setattr(main.config, 'reload', lambda: [new_job])

    main.sync_jobs()

    scheduled = scheduler.get_job('foobar')
    assert str(scheduled.trigger) == str(CronTrigger.from_crontab(new_job.schedule))
    assert main.jobs == [new_job]


def test_sync_jobs_leaves_unchanged_job_untouched(monkeypatch, config):
    from scheduler import main

    scheduler = _fresh_scheduler(monkeypatch, main)
    job = Job(name='foobar', jobtype='run', schedule='* * * * *')
    main._add_job(job)
    monkeypatch.setattr(main, 'jobs', [job])

    calls = []
    monkeypatch.setattr(scheduler, 'remove_job', lambda *a, **kw: calls.append('remove'))
    orig_add_job = scheduler.add_job
    def spy_add_job(*a, **kw):
        calls.append('add')
        return orig_add_job(*a, **kw)
    monkeypatch.setattr(scheduler, 'add_job', spy_add_job)

    same_job = Job(name='foobar', jobtype='run', schedule='* * * * *')
    monkeypatch.setattr(main.config, 'reload', lambda: [same_job])

    main.sync_jobs()

    assert calls == []
    assert main.jobs == [same_job]


def test_sync_jobs_invalid_config_is_noop(monkeypatch, config):
    from scheduler import main

    scheduler = _fresh_scheduler(monkeypatch, main)
    job = Job(name='foobar', jobtype='run', schedule='* * * * *')
    main._add_job(job)
    monkeypatch.setattr(main, 'jobs', [job])
    monkeypatch.setattr(main.config, 'reload', lambda: None)

    main.sync_jobs()

    assert {j.id for j in scheduler.get_jobs()} == {'foobar'}
    assert main.jobs == [job]


def test_run_job_failure(monkeypatch, config):
    from scheduler import main

    class mock_docker:
        def start_run(job):
            raise KeyError('AWS_SECRET')  # e.g. a missing ${ENV_VAR} placeholder

    class mock_logger:
        def info(self, message, *args):
            pass

        def error(self, message, *args):
            assert 'foobar' in args

    monkeypatch.setattr(main, 'docker', mock_docker)
    monkeypatch.setattr(main, 'logger', mock_logger())

    job = Job(
        name='foobar',
        jobtype='run',
        schedule='foobar'
    )
    main.run_job(job)
