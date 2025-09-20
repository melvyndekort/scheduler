import pytest
import os

def test_send(monkeypatch):
    os.environ['NTFY_URL'] = "https://localhost/topic"
    os.environ['NTFY_TOKEN'] = "test_token"
    from scheduler import notify

    called = False
    def mock_post(url, data, headers):
        nonlocal called
        called = True
        assert url == 'https://localhost/topic'
        assert data == 'foobar'
        assert headers['Authorization'] == 'Bearer test_token'

    monkeypatch.setattr(notify.requests, 'post', mock_post)
    
    notify.notify('foobar')
    assert called
