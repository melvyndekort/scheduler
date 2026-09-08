import pytest
import os

def test_send(monkeypatch):
    os.environ['APPRISE_URL'] = "https://localhost"
    os.environ['APPRISE_TAG'] = "test"
    os.environ['APPRISE_KEY'] = "mykey"
    from scheduler import notify

    called = False
    def mock_post(url, json, timeout):
        nonlocal called
        called = True
        assert url == 'https://localhost/notify/mykey'
        assert json['body'] == 'foobar'
        assert json['tag'] == 'test'
        assert timeout == 10

    monkeypatch.setattr(notify.requests, 'post', mock_post)

    notify.notify('foobar')
    assert called


def test_send_swallows_connection_failure(monkeypatch):
    """A dead/unreachable Apprise endpoint must not raise - callers rely on
    their own exception surviving notify(), not one about the notification."""
    os.environ['APPRISE_URL'] = "https://localhost"
    from scheduler import notify

    def mock_post(url, json, timeout):
        raise notify.requests.exceptions.ConnectionError('unreachable')

    monkeypatch.setattr(notify.requests, 'post', mock_post)

    notify.notify('foobar')  # must not raise
