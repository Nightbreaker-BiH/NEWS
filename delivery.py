"""
delivery.py — Slanje izvještaja putem emaila i/ili Telegrama
"""

import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Gmail SMTP
# ---------------------------------------------------------------------------
def send_email(subject: str, html_body: str, plain_body: str) -> bool:
    """
    Šalje HTML email putem Gmail SMTP-a.
    Zahtijeva 'App Password' (ne Google nalog lozinku).
    """
    gmail_user  = os.getenv("GMAIL_USER")
    gmail_pass  = os.getenv("GMAIL_APP_PASSWORD")
    recipient   = os.getenv("RECIPIENT_EMAIL", gmail_user)

    if not gmail_user or not gmail_pass:
        logger.error("GMAIL_USER ili GMAIL_APP_PASSWORD nisu postavljeni.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Daily Digest <{gmail_user}>"
    msg["To"]      = recipient

    msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body,  "html",  "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, recipient, msg.as_string())
        logger.info(f"✅ Email uspješno poslan na {recipient}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("❌ Gmail autentifikacija neuspješna — provjerite App Password.")
        return False
    except Exception as e:
        logger.error(f"❌ Greška pri slanju emaila: {e}")
        return False


# ---------------------------------------------------------------------------
# Telegram Bot
# ---------------------------------------------------------------------------
def send_telegram(message: str) -> bool:
    """
    Šalje poruku putem Telegram Bota.
    Alternativa / backup za email.
    """
    import requests as req

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id   = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logger.warning("Telegram nije konfigurisan — preskačem.")
        return False

    url  = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id":    chat_id,
        "text":       message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    # Telegram ima limit od 4096 znakova po poruci — splituj ako treba
    if len(message) > 4000:
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    else:
        chunks = [message]

    success = True
    for chunk in chunks:
        data["text"] = chunk
        try:
            resp = req.post(url, json=data, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"❌ Telegram greška: {e}")
            success = False

    if success:
        logger.info("✅ Telegram poruka uspješno poslana.")
    return success


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------
def deliver(html_body: str, plain_body: str, telegram_body: str) -> None:
    """Šalje izvještaj prema konfiguriranoj metodi."""
    method  = os.getenv("DELIVERY_METHOD", "email").lower()
    today   = datetime.now().strftime("%d.%m.%Y")
    subject = f"📋 Dnevni izvještaj — {today}"

    if method in ("email", "both"):
        send_email(subject, html_body, plain_body)

    if method in ("telegram", "both"):
        send_telegram(telegram_body)
