
import logging
import os

import requests

logger = logging.getLogger(__name__)


def send_knowledge_gap_event(payload: dict) -> None:
    """Send a knowledge-gap event to n8n without interrupting the chatbot."""
    from config.settings import settings

    webhook_url = settings.N8N_KNOWLEDGE_GAP_WEBHOOK_URL

    if not webhook_url:
        logger.warning("n8n webhook URL is not configured.")
        return

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=3,
        )
        response.raise_for_status()
        logger.info("Knowledge-gap event sent to n8n successfully.")

    except requests.RequestException:
        logger.exception("Failed to send knowledge-gap event to n8n.")
