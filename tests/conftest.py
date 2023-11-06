import os
import pytest

@pytest.fixture
def config(tmpdir):
    config = f'{tmpdir}/config.yml'
    with open(config, "w") as file:
        file.write('''
jobs:
  - name: 'foobar'
    jobtype: 'run'
    schedule: '* * * * *'
''')
    os.environ['CONFIG'] = config
    return config
