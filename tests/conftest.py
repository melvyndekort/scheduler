import importlib
import os
import pytest

DEFAULT_CONFIG_YAML = '''
jobs:
  - name: 'foobar'
    jobtype: 'run'
    schedule: '* * * * *'
'''


@pytest.fixture
def config(tmpdir):
    config = f'{tmpdir}/config.yml'
    with open(config, "w") as file:
        file.write(DEFAULT_CONFIG_YAML)
    os.environ['CONFIG'] = config
    return config


@pytest.fixture
def config_module(config):
    """The scheduler.config module, reloaded against this test's own config
    file so each test starts from a clean, isolated baseline.

    scheduler.config caches its state at module level, so any test that
    calls reload() to mutate it must not leak that state into later tests
    (e.g. scheduler.main snapshots config.get_jobs() at import time). This
    fixture restores known-good content on teardown for exactly that reason.
    """
    from scheduler import config as module
    importlib.reload(module)
    yield module
    with open(module.CONFIG_PATH, 'w') as file:
        file.write(DEFAULT_CONFIG_YAML)
    module.reload()
