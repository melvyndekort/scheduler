import pytest
import os

from scheduler import job


def test_is_running(monkeypatch):
  myJob = job.Job(
    name='foobar',
    jobtype='run',
    schedule='always'
  )

  class MockDocker:
    @staticmethod
    def is_running(name):
      assert name == 'foobar'
      return True

  monkeypatch.setattr(job, 'docker', MockDocker)
  assert myJob.is_running() == True

def test_get_image():
  myJob = job.Job(
    name='foobar',
    jobtype='run',
    schedule='always',
    image='image',
    container='container'
  )

  assert myJob.get_image_or_container() == 'image'

def test_get_container():
  myJob = job.Job(
    name='foobar',
    jobtype='exec',
    schedule='always',
    image='image',
    container='container'
  )

  assert myJob.get_image_or_container() == 'container'
