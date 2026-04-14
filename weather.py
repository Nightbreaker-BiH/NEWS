"""
weather.py — Dohvatanje vremenske prognoze za Sarajevo
Koristi OpenWeatherMap API (besplatni tier).
"""

import os
import requests
from datetime import datetime

CITY   = "Sarajevo"
LAT    = 43.8563
LON    = 18.4131
UNITS  = "metric"
LANG   = "hr"

CONDITION_ICONS = {
    "Thunderstorm": "⛈️", "Drizzle": "🌦️", "Rain": "🌧️",
    "Snow": "❄️", "Clear": "☀️", "Clouds": "☁️",
    "Mist": "🌫️", "Fog": "🌫️", "Haze": "🌫️",
}

def _get_icon(main):
    return CONDITION_ICONS.get(main, "🌡️")


def fetch_weather():
    api_key = os.getenv("OPENWEATHER_API_KEY")

    # Ako nema API ključa ili ključ nije aktivan — vrati placeholder
    if not api_key:
        return _placeholder()

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={LAT}&lon={LON}&appid={api_key}&units={UNITS}&lang={LANG}"
    )
    fore_url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={LAT}&lon={LON}&appid={api_key}&units={UNITS}&lang={LANG}&cnt=8"
    )

    try:
        cur  = requests.get(url,      timeout=10).json()
        fore = requests.get(fore_url, timeout=10).json()

        # Provjeri da li API vraca grešku (neaktivan ključ, itd.)
        if "main" not in cur:
            error_msg = cur.get("message", "API greška")
            print(f"[UPOZORENJE] OpenWeatherMap: {error_msg} — koristim placeholder podatke")
            return _placeholder()

        today_temps = [i["main"]["temp"] for i in fore.get("list", [])]
        sunrise = datetime.fromtimestamp(cur["sys"]["sunrise"]).strftime("%H:%M")
        sunset  = datetime.fromtimestamp(cur["sys"]["sunset"]).strftime("%H:%M")

        return {
            "city":        CITY,
            "icon":        _get_icon(cur["weather"][0]["main"]),
            "temp":        round(cur["main"]["temp"]),
            "feels_like":  round(cur["main"].get("feels_like", cur["main"]["temp"])),
            "temp_min":    round(min(today_temps)) if today_temps else round(cur["main"]["temp_min"]),
            "temp_max":    round(max(today_temps)) if today_temps else round(cur["main"]["temp_max"]),
            "description": cur["weather"][0]["description"].capitalize(),
            "humidity":    cur["main"].get("humidity", 0),
            "wind_kmh":    round(cur.get("wind", {}).get("speed", 0) * 3.6, 1),
            "sunrise":     sunrise,
            "sunset":      sunset,
        }

    except Exception as e:
        print(f"[UPOZORENJE] Greška pri dohvatanju vremena: {e} — koristim placeholder")
        return _placeholder()


def _placeholder():
    """Vraća placeholder podatke kada API nije dostupan."""
    return {
        "city":        CITY,
        "icon":        "🌤️",
        "temp":        "N/A",
        "feels_like":  "N/A",
        "temp_min":    "N/A",
        "temp_max":    "N/A",
        "description": "Prognoza nedostupna (API ključ se aktivira)",
        "humidity":    "N/A",
        "wind_kmh":    "N/A",
        "sunrise":     "N/A",
        "sunset":      "N/A",
    }
