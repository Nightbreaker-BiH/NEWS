"""
main.py — Glavna skripta: scheduler + orchestracija

Pokretanje:
    python main.py              # Kontinuirani daemon (preporučeno)
    python main.py --now        # Jednokratno slanje odmah (testiranje)
    python main.py --cron       # Samo jednom, za cron job integraciju
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Učitaj .env odmah
load_dotenv()

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from weather  import fetch_weather
from news     import fetch_all_news
from report   import build_html_report, build_plain_report, build_telegram_report
from delivery import deliver

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler("daily_digest.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")

TIMEZONE = pytz.timezone("Europe/Sarajevo")


# ---------------------------------------------------------------------------
# Glavni posao
# ---------------------------------------------------------------------------
def run_daily_digest() -> None:
    start = datetime.now()
    logger.info("=" * 55)
    logger.info(f"🚀 Pokretanje dnevnog sažetka — {start.strftime('%d.%m.%Y %H:%M')}")

    try:
        # 1. Vremenska prognoza
        logger.info("📡 Dohvatanje vremenske prognoze...")
        weather = fetch_weather()
        logger.info(f"   Sarajevo: {weather['temp']}°C, {weather['description']}")

        # 2. Vijesti
        logger.info("📰 Dohvatanje vijesti...")
        news = fetch_all_news()

        # 3. Generisanje izvještaja
        logger.info("📝 Generisanje izvještaja...")
        html_body     = build_html_report(weather, news)
        plain_body    = build_plain_report(weather, news)
        telegram_body = build_telegram_report(weather, news)

        # 4. Isporuka
        logger.info("📤 Isporuka...")
        deliver(html_body, plain_body, telegram_body)

        elapsed = (datetime.now() - start).total_seconds()
        logger.info(f"✅ Završeno za {elapsed:.1f}s")

    except Exception as e:
        logger.exception(f"❌ Kritična greška: {e}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    args = sys.argv[1:]

    if "--now" in args or "--cron" in args:
        # Jednokratno pokretanje (test ili cron)
        run_daily_digest()

    else:
        # Daemon mod: scheduler čeka 07:30 svaki dan
        scheduler = BlockingScheduler(timezone=TIMEZONE)
        scheduler.add_job(
            func    = run_daily_digest,
            trigger = CronTrigger(hour=7, minute=30, timezone=TIMEZONE),
            id      = "daily_digest",
            name    = "Dnevni sažetak",
            misfire_grace_time = 900,  # Toleriše kašnjenje do 15 min
        )

        logger.info("⏰ Scheduler pokrenuti — slanje u 07:30 (Europe/Sarajevo)")
        logger.info("   Pritisnite Ctrl+C za zaustavljanje.")

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("🛑 Scheduler zaustavljeni.")
