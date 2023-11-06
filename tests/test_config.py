import pytest
import yaml
import os
import importlib


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
