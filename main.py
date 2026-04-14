"""
main.py — Orchestracija dnevnog sažetka.
Pokretanje: python main.py        (daemon, čeka 07:30 / 19:30)
            python main.py --now  (odmah, za testiranje)
            python main.py --cron (jednom, za GitHub Actions)
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from weather     import fetch_weather
from news        import fetch_all_news
from astro_local import get_astro_data
from report      import build_html_report, build_plain_report, build_telegram_report
from delivery    import deliver

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler("daily_digest.log", encoding="utf-8"),
    ],
)
logger   = logging.getLogger("main")
TIMEZONE = pytz.timezone("Europe/Sarajevo")


def run_daily_digest():
    start = datetime.now()
    logger.info("=" * 55)
    logger.info(f"🚀 Pokretanje — {start.strftime('%d.%m.%Y %H:%M')}")

    try:
        # 1. Prognoza
        logger.info("📡 Prognoza...")
        weather = fetch_weather()
        logger.info(f"   {weather['temp']}°C, {weather['description']}, oblačnost: {weather['cloud_pct']}%")

        # 2. Vijesti
        logger.info("📰 Vijesti...")
        news = fetch_all_news()

        # 3. Kategorije bez vijesti → greška
        errors = [
            f"{k} (0 članaka)"
            for k, v in news.items()
            if not v
        ]
        if errors:
            logger.warning(f"   Prazne kategorije: {', '.join(errors)}")

        # 4. Astronomski podaci
        logger.info("🔭 Astronomski podaci...")
        astro = get_astro_data(weather_data=weather)
        if astro.get('error'):
            logger.warning(f"   Astro greška: {astro['error']}")
        else:
            visible = [p['name'] for p in astro.get('visible_planets', [])]
            logger.info(f"   Vidljive planete: {', '.join(visible) or 'nema'}")
            logger.info(f"   Seeing: {astro.get('seeing_score')}/5")

        # 5. Generisanje izvještaja
        logger.info("📝 Generisanje izvještaja...")
        html_body     = build_html_report(weather, news, astro=astro, errors=errors)
        plain_body    = build_plain_report(weather, news, astro=astro, errors=errors)
        telegram_body = build_telegram_report(weather, news, astro=astro, errors=errors)

        # 6. Isporuka
        logger.info("📤 Isporuka...")
        deliver(html_body, plain_body, telegram_body, weather=weather)

        elapsed = (datetime.now() - start).total_seconds()
        logger.info(f"✅ Završeno za {elapsed:.1f}s")

    except Exception as e:
        logger.exception(f"❌ Kritična greška: {e}")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--now" in args or "--cron" in args:
        run_daily_digest()
    else:
        scheduler = BlockingScheduler(timezone=TIMEZONE)

        # Jutarnje — 07:30
        scheduler.add_job(
            run_daily_digest,
            CronTrigger(hour=7, minute=30, timezone=TIMEZONE),
            id="jutarnji", name="Jutarnji sažetak",
            misfire_grace_time=900,
        )
        # Večernje — 19:30
        scheduler.add_job(
            run_daily_digest,
            CronTrigger(hour=19, minute=30, timezone=TIMEZONE),
            id="vecernji", name="Večernji sažetak",
            misfire_grace_time=900,
        )

        logger.info("⏰ Scheduler: 07:30 jutarnji / 19:30 večernji (Europe/Sarajevo)")
        logger.info("   Ctrl+C za zaustavljanje.")

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("🛑 Zaustavljeno.")
