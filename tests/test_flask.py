"""Tests for Flask endpoints."""
import pytest


def test_health_endpoint(config):
    """Test health endpoint returns 200 OK."""
    # Import after config is set up
    from scheduler.flask import app

    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json == {'status': 'ok'}


def test_index_reflects_config_changes_without_restart(config_module):
    """Editing config.yml should be visible on the next request, no restart."""
    from scheduler.flask import app, webroot

    with app.test_client() as client:
        response = client.get(webroot)
        assert b'* * * * *' in response.data

        with open(config_module.CONFIG_PATH, 'w') as f:
            f.write('''
jobs:
  - name: 'updated-job'
    jobtype: 'run'
    schedule: '5 5 * * *'
''')

        response = client.get(webroot)
        assert b'5 5 * * *' in response.data
        assert b'* * * * *' not in response.data


def test_post_trigger_success(config_module, monkeypatch):
    """Triggering a job re-reads config.yml, so a live edit takes effect."""
    from scheduler import flask as flask_module

    monkeypatch.setattr(flask_module.docker, 'execute', lambda job: True)

    with flask_module.app.test_client() as client:
        response = client.post(flask_module.webroot, data={'triggerJobName': 'foobar'})
        assert response.status_code == 200
        assert b'successfully triggered' in response.data


def test_post_trigger_failure(config_module, monkeypatch):
    from scheduler import flask as flask_module

    monkeypatch.setattr(flask_module.docker, 'execute', lambda job: False)

    with flask_module.app.test_client() as client:
        response = client.post(flask_module.webroot, data={'triggerJobName': 'foobar'})
        assert response.status_code == 200
        assert b'could not be triggered' in response.data


def test_post_trigger_missing_jobname(config_module):
    from scheduler import flask as flask_module

    with flask_module.app.test_client() as client:
        response = client.post(flask_module.webroot, data={})
        assert response.status_code == 200
        assert b'No valid job was triggered' in response.data


def test_post_trigger_unknown_jobname(config_module):
    """A job removed from config.yml between page load and submit should
    show an error, not crash (docker.execute(None) would otherwise blow up)."""
    from scheduler import flask as flask_module

    with flask_module.app.test_client() as client:
        response = client.post(flask_module.webroot, data={'triggerJobName': 'gone'})
        assert response.status_code == 200
        assert b'no longer exists' in response.data
