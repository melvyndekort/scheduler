"""Notification module for sending alerts via Apprise API."""
import logging
import os
import requests

logger = logging.getLogger(__name__)


def notify(message):
    """Send notification message via Apprise API.
    
    Args:
        message: The notification message to send
    """
    if 'APPRISE_URL' in os.environ:
        url = os.environ['APPRISE_URL'].rstrip('/')
        tag = os.environ.get('APPRISE_TAG', 'homelab')
        key = os.environ.get('APPRISE_KEY', 'apprise')

        payload = {
            'body': message,
            'tag': tag
        }
        requests.post(f'{url}/notify/{key}', json=payload, timeout=10)
    else:
        logger.error('APPRISE_URL is not configured')
