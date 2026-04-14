"""
delivery.py — Slanje emaila s personalizovanim subjectom.
Subject: 🌧️ 14°C | Jutarnji izvještaj — Utorak 14. april
"""

import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger(__name__)

DAYS_BS   = ["Ponedjeljak","Utorak","Srijeda","Četvrtak","Petak","Subota","Nedjelja"]
MONTHS_BS = ["januara","februara","marta","aprila","maja","juna",
             "jula","augusta","septembra","oktobra","novembra","decembra"]


def _build_subject(weather):
    """Gradi personalizovani subject sa temperaturom i datumom."""
    now  = datetime.now()
    icon = weather.get('icon', '🌡️')
    temp = weather.get('temp', 'N/A')
    day  = DAYS_BS[now.weekday()]

    # Jutarnji / Večernji
    edition = "Jutarnji" if now.hour < 12 else "Večernji"

    return f"{icon} {temp}°C | {edition} izvještaj — {day} {now.day}. {MONTHS_BS[now.month-1]}"


def send_email(html_body: str, plain_body: str, weather: dict) -> bool:
    gmail_user  = os.getenv("GMAIL_USER")
    gmail_pass  = os.getenv("GMAIL_APP_PASSWORD")
    recipients_raw = os.getenv("RECIPIENT_EMAIL", gmail_user)

    if not gmail_user or not gmail_pass:
        logger.error("GMAIL_USER ili GMAIL_APP_PASSWORD nisu postavljeni.")
        return False

    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
    subject    = _build_subject(weather)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Daily Digest BiH <{gmail_user}>"
    msg["To"]      = ", ".join(recipients)

    msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body,  "html",  "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, recipients, msg.as_string())
        logger.info(f"✅ Email poslan na: {', '.join(recipients)}")
        logger.info(f"   Subject: {subject}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("❌ Gmail Auth greška — provjerite App Password.")
        return False
    except Exception as e:
        logger.error(f"❌ Email greška: {e}")
        return False


def send_telegram(message: str) -> bool:
    import requests as req
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id   = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logger.warning("Telegram nije konfigurisan.")
        return False

    url    = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]

    for chunk in chunks:
        try:
            resp = req.post(url, json={
                "chat_id": chat_id, "text": chunk,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"❌ Telegram: {e}")
            return False

    logger.info("✅ Telegram poruka poslana.")
    return True


def deliver(html_body: str, plain_body: str, telegram_body: str,
            weather: dict) -> None:
    method = os.getenv("DELIVERY_METHOD", "email").lower()
    if method in ("email", "both"):
        send_email(html_body, plain_body, weather)
    if method in ("telegram", "both"):
        send_telegram(telegram_body)
