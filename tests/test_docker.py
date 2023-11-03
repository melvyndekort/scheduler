import pytest
import docker

from scheduler import docker as sut
from scheduler.job import Job

@pytest.fixture
def docker_mock():
  class MockContainer():
    id = 42
    short_id = 42

  class MockContainers():
    def get(self, name):
      if name == 'success':
        return True
      elif name == 'failure':
        raise docker.errors.NotFound('failure')
      elif name == 'exec-container':
        return MockContainer()

    def run(self, **kwargs):
      assert kwargs.get('image') == 'run-image'
      return MockContainer()

  class MockApi():
    def exec_create(self, container, cmd, user):
      assert container == 42
      assert cmd == 'exec-command'
      assert user == None
      return 'exec-id'

    def exec_start(self, exec_id, detach):
      assert exec_id == 'exec-id'
      assert detach

  class MockClient():
    containers = MockContainers()
    api = MockApi()
  
  return MockClient()


def test_is_running_success(monkeypatch, docker_mock):
  monkeypatch.setattr(sut, 'client', docker_mock)

  result = sut.is_running('success')
  assert result

def test_is_running_fail(monkeypatch, docker_mock):
  monkeypatch.setattr(sut, 'client', docker_mock)

  result = sut.is_running('failure')
  assert not result

def test_start_exec(monkeypatch, docker_mock):
  monkeypatch.setattr(sut, 'client', docker_mock)
  job = Job(
    name='exec-name',
    jobtype='exec',
    schedule='exec-schedule',
    container='exec-container',
    command='exec-command'
  )
  sut.start_exec(job)

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
