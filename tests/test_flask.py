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
