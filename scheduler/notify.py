import logging
import os

from slack_sdk.webhook import WebhookClient

logger = logging.getLogger(__name__)


def notify(message):
    if 'SLACK_WEBHOOK' in os.environ:
        webhook = os.environ['SLACK_WEBHOOK']
        client = WebhookClient(webhook)

        response = client.send(
            text=message,
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': message
                    }
                }
            ]
        )
    else:
        logger.error('Slack webhook is not configured')
