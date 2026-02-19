import pytest
import docker
import os

os.environ['NTFY_URL'] = 'https://localhost/topic'
os.environ['NTFY_TOKEN'] = 'test_token'

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
                class RunningContainer:
                    status = 'running'
                return RunningContainer()
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

def test_is_running_stopped(monkeypatch, docker_mock):
    monkeypatch.setattr(sut, 'client', docker_mock)
    
    class StoppedContainer:
        status = 'exited'
    
    class MockContainers:
        def get(self, name):
            return StoppedContainer()
    
    class MockClient:
        containers = MockContainers()
    
    monkeypatch.setattr(sut, 'client', MockClient())
    result = sut.is_running('stopped')
    assert not result

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

def test_start_run_with_env_file(monkeypatch, docker_mock):
    monkeypatch.setattr(sut, 'client', docker_mock)
    
    called = False
    def mock_run(**kwargs):
        nonlocal called
        called = True
        assert kwargs.get('env_file') == ['/path/to/secrets.env']
        class MockContainer:
            short_id = 42
        return MockContainer()
    
    docker_mock.containers.run = mock_run
    
    job = Job(
        name='run-name',
        jobtype='run',
        schedule='run-schedule',
        image='run-image',
        env_file=['/path/to/secrets.env']
    )
    result = sut.start_run(job)
    assert result == 42
    assert called

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
