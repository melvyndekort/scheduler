import pytest
import os

def test_send(monkeypatch):
    os.environ['SLACK_WEBHOOK'] = "https://localhost"
    from scheduler import notify

    called = False
    class mock_slack:
        def __init__(self, url):
            pass

        def send(self, text, blocks):
            nonlocal called
            called = True
            assert text == 'foobar'

    monkeypatch.setattr(notify, 'WebhookClient', mock_slack)
    
    notify.notify('foobar')
    assert called
