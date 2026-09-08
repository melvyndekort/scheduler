import pytest
import yaml
import os


def test_webroot_env(config):
    os.environ['WEBROOT'] = '/foobar'
    from scheduler import config

    webroot = config.get_webroot()

    assert webroot == '/foobar'

def test_get_jobs(config):
    from scheduler import config

    jobs = config.get_jobs()

    assert len(jobs) == 1
    assert jobs[0].name == 'foobar'


def test_reload_updates_jobs(config_module):
    with open(config_module.CONFIG_PATH, 'w') as f:
        f.write('''
jobs:
  - name: 'updated'
    jobtype: 'run'
    schedule: '5 5 * * *'
''')

    new_jobs = config_module.reload()

    assert new_jobs is not None
    assert [j.name for j in new_jobs] == ['updated']
    assert [j.name for j in config_module.get_jobs()] == ['updated']


def test_reload_invalid_yaml_keeps_last_known_good(config_module):
    good_jobs = config_module.get_jobs()

    with open(config_module.CONFIG_PATH, 'w') as f:
        f.write('jobs: [unclosed')

    result = config_module.reload()

    assert result is None
    assert config_module.get_jobs() == good_jobs


def test_reload_malformed_job_keeps_last_known_good(config_module):
    good_jobs = config_module.get_jobs()

    with open(config_module.CONFIG_PATH, 'w') as f:
        f.write('''
jobs:
  - name: 'missing-required-fields'
''')

    result = config_module.reload()

    assert result is None
    assert config_module.get_jobs() == good_jobs
