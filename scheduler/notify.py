import logging
import os
import requests

logger = logging.getLogger(__name__)


def notify(message):
    if 'NTFY_URL' in os.environ and 'NTFY_TOKEN' in os.environ:
        url = os.environ['NTFY_URL']
        token = os.environ['NTFY_TOKEN']
        
        headers = {'Authorization': f'Bearer {token}'}
        requests.post(url, data=message, headers=headers)
    else:
        logger.error('NTFY_URL or NTFY_TOKEN is not configured')
