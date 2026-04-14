"""
weather.py — Vremenska prognoza za Sarajevo.
Danas + 3-dnevna prognoza + podaci za seeing procjenu.
"""

import os
import logging
import requests
from datetime import datetime, timedelta
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

LAT   = 43.8563
LON   = 18.4131
UNITS = "metric"
LANG  = "hr"

DAYS_BS = ["Ponedjeljak","Utorak","Srijeda","Četvrtak","Petak","Subota","Nedjelja"]

ICONS = {
    "Thunderstorm": "⛈️", "Drizzle": "🌦️", "Rain": "🌧️",
    "Snow": "❄️", "Clear": "☀️", "Clouds": "☁️",
    "Mist": "🌫️", "Fog": "🌫️", "Haze": "🌫️",
    "Smoke": "🌫️", "Dust": "🌪️", "Tornado": "🌪️",
}

def _icon(main): return ICONS.get(main, "🌡️")


def fetch_weather():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return _placeholder()

    cur_url  = (f"https://api.openweathermap.org/data/2.5/weather"
                f"?lat={LAT}&lon={LON}&appid={api_key}&units={UNITS}&lang={LANG}")
    fore_url = (f"https://api.openweathermap.org/data/2.5/forecast"
                f"?lat={LAT}&lon={LON}&appid={api_key}&units={UNITS}&lang={LANG}&cnt=40")
    try:
        cur  = requests.get(cur_url,  timeout=10).json()
        fore = requests.get(fore_url, timeout=10).json()

        if "main" not in cur:
            logger.warning(f"OWM: {cur.get('message','API greška')} — placeholder")
            return _placeholder()

        # ── Danas ─────────────────────────────────────────────
        today_items = [i for i in fore.get("list", [])
                       if datetime.fromtimestamp(i["dt"]).date() == datetime.now().date()]
        all_items   = fore.get("list", [])

        temps       = [i["main"]["temp"] for i in (today_items or all_items[:8])]
        cloud_pct   = cur.get("clouds", {}).get("all", 100)
        wind_ms     = cur.get("wind", {}).get("speed", 0)
        humidity    = cur["main"].get("humidity", 0)
        sunrise     = datetime.fromtimestamp(cur["sys"]["sunrise"]).strftime("%H:%M")
        sunset      = datetime.fromtimestamp(cur["sys"]["sunset"]).strftime("%H:%M")

        # ── 3-dnevna prognoza ─────────────────────────────────
        days = defaultdict(list)
        for item in all_items:
            days[datetime.fromtimestamp(item["dt"]).date()].append(item)

        forecast_3day = []
        today = datetime.now().date()
        for offset in range(1, 4):
            target = today + timedelta(days=offset)
            items  = days.get(target, [])
            if not items:
                continue
            t = [i["main"]["temp"] for i in items]
            mains = [i["weather"][0]["main"] for i in items]
            descs = [i["weather"][0]["description"] for i in items]
            main_w = Counter(mains).most_common(1)[0][0]
            forecast_3day.append({
                "day_name":    DAYS_BS[target.weekday()],
                "date_str":    target.strftime("%d.%m."),
                "temp_min":    round(min(t)),
                "temp_max":    round(max(t)),
                "icon":        _icon(main_w),
                "description": Counter(descs).most_common(1)[0][0].capitalize(),
            })

        return {
            "city":           "Sarajevo",
            "icon":           _icon(cur["weather"][0]["main"]),
            "temp":           round(cur["main"]["temp"]),
            "feels_like":     round(cur["main"].get("feels_like", cur["main"]["temp"])),
            "temp_min":       round(min(temps)) if temps else "N/A",
            "temp_max":       round(max(temps)) if temps else "N/A",
            "description":    cur["weather"][0]["description"].capitalize(),
            "humidity":       humidity,
            "wind_kmh":       round(wind_ms * 3.6, 1),
            "cloud_pct":      cloud_pct,
            "sunrise":        sunrise,
            "sunset":         sunset,
            "forecast_3day":  forecast_3day,
        }

    except Exception as e:
        logger.error(f"Greška pri dohvatanju vremena: {e}")
        return _placeholder()


def _placeholder():
    return {
        "city": "Sarajevo", "icon": "🌤️",
        "temp": "N/A", "feels_like": "N/A",
        "temp_min": "N/A", "temp_max": "N/A",
        "description": "Prognoza nedostupna (API ključ se aktivira do 2h)",
        "humidity": "N/A", "wind_kmh": "N/A",
        "cloud_pct": 100, "sunrise": "N/A", "sunset": "N/A",
        "forecast_3day": [],
    }
