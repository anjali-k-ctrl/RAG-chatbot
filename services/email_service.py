
import os
import smtplib
import logging
from pathlib import Path
from email.message import EmailMessage

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)


def send_knowledge_gap_email(payload: dict) -> None:
    sender = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_APP_PASSWORD")
    recipient = os.getenv("KNOWLEDGE_GAP_EMAIL_TO")

    if not sender or not password or not recipient:
        raise RuntimeError(
            "Email configuration missing. Check SMTP_EMAIL, "
            "SMTP_APP_PASSWORD, and KNOWLEDGE_GAP_EMAIL_TO in .env."
        )

    msg = EmailMessage()
    msg["Subject"] = "[MediaShippers] Knowledge Gap Detected"
    msg["From"] = sender
    msg["To"] = recipient

    msg.set_content(
        f"""A knowledge gap was detected.

Question: {payload.get('question', 'N/A')}
Audience: {payload.get('audience', 'N/A')}
Page: {payload.get('page_name', 'N/A')}
Retrieval score: {payload.get('score', 'N/A')}
Knowledge gap: {payload.get('knowledge_gap', 'N/A')}
Prompt ID: {payload.get('prompt_id', 'N/A')}
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
        smtp.login(sender, password.replace(" ", ""))
        smtp.send_message(msg)

    logger.info("Knowledge-gap email sent to %s", recipient)
