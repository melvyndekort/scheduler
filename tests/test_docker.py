import pytest
import docker
import os

os.environ['SLACK_WEBHOOK'] = 'foobar'

from scheduler import docker as sut
from scheduler.job import Job


@pytest.fixture
def docker_mock():
    class MockContainer():
        id = 42
        short_id = 42

        def exec_run(self, cmd, **kwargs):
            assert cmd == 'exec-command'
            assert kwargs.get('user') == ''

    class MockContainers():
        def get(self, name):
            if name == 'success':
                return True
            elif name in ['failure','exec-container-fail']:
                raise docker.errors.NotFound('failure')
            elif name == 'exec-container':
                return MockContainer()

        def run(self, **kwargs):
            if kwargs.get('image') == 'run-image-fail':
                raise docker.errors.ContainerError
            assert kwargs.get('image') == 'run-image'
            return MockContainer()

    class MockClient():
        containers = MockContainers()
    
    return MockClient()


def test_is_running_success(monkeypatch, docker_mock):
    monkeypatch.setattr(sut, 'client', docker_mock)

    result = sut.is_running('success')
    assert result

def test_is_running_fail(monkeypatch, docker_mock):
    monkeypatch.setattr(sut, 'client', docker_mock)

    result = sut.is_running('failure')
    assert not result

def test_start_exec_success(monkeypatch, docker_mock):
    monkeypatch.setattr(sut, 'client', docker_mock)
    job = Job(
        name='exec-name',
        jobtype='exec',
        schedule='exec-schedule',
        container='exec-container',
        command='exec-command'
    )
    sut.start_exec(job)

def test_start_exec_fail(monkeypatch, docker_mock):
    monkeypatch.setattr(sut, 'client', docker_mock)

    called = False
    class notify_mock:
        def notify(self, message):
            nonlocal called
            called = True
            assert 'Executing command in exec-container-fail failed:' in message
    monkeypatch.setattr(sut, 'notify', notify_mock())

    job = Job(
        name='exec-name',
        jobtype='exec',
        schedule='exec-schedule',
        container='exec-container-fail',
        command='exec-command-fail'
    )
    with pytest.raises(docker.errors.NotFound):
        sut.start_exec(job)
    assert called

def test_start_run(monkeypatch, docker_mock):
    monkeypatch.setattr(sut, 'client', docker_mock)
    job = Job(
        name='run-name',
        jobtype='run',
        schedule='run-schedule',
        image='run-image'
    )
    result = sut.start_run(job)
    assert result == 42

def test_start_run_failed(monkeypatch, docker_mock):
    monkeypatch.setattr(sut, 'client', docker_mock)

    called = False
    class notify_mock:
        def notify(self, message):
            nonlocal called
            called = True
            assert message == 'Running container run-name failed'
    monkeypatch.setattr(sut, 'notify', notify_mock())

    job = Job(
        name='run-name',
        jobtype='run',
        schedule='run-schedule',
        image='run-image-fail'
    )
    with pytest.raises(Exception):
        result = sut.start_run(job)
    assert called

def test_replace_environment():
    os.environ['FOOBAR'] = 'testval'
    os.environ['FOOBAR2'] = 'testval2'
    envlist = ['foobar=${FOOBAR}', 'foobar2=${FOOBAR2}', 'foobar3=testval3']

    envlist = sut.replace_environment(envlist)

    assert envlist[0] == 'foobar=testval'
    assert envlist[1] == 'foobar2=testval2'
    assert envlist[2] == 'foobar3=testval3'
