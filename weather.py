"""
weather.py — Dohvatanje vremenske prognoze za Sarajevo
Koristi OpenWeatherMap One Call API (besplatni tier).
"""

import os
import requests
from datetime import datetime

CITY    = "Sarajevo"
LAT     = 43.8563
LON     = 18.4131
UNITS   = "metric"
LANG    = "hr"   # Hrvatski jezik u opisima

CONDITION_ICONS = {
    "Thunderstorm": "⛈️",
    "Drizzle":      "🌦️",
    "Rain":         "🌧️",
    "Snow":         "❄️",
    "Clear":        "☀️",
    "Clouds":       "☁️",
    "Mist":         "🌫️",
    "Fog":          "🌫️",
    "Haze":         "🌫️",
    "Smoke":        "🌫️",
    "Dust":         "🌪️",
    "Sand":         "🌪️",
    "Ash":          "🌋",
    "Squall":       "💨",
    "Tornado":      "🌪️",
}

def _get_icon(main: str) -> str:
    return CONDITION_ICONS.get(main, "🌡️")


def fetch_weather() -> dict:
    """Vraća rječnik sa podacima o prognozi za danas."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY nije postavljen u .env")

    # Current weather
    current_url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={LAT}&lon={LON}&appid={api_key}&units={UNITS}&lang={LANG}"
    )
    # 5-day / 3-hour forecast
    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={LAT}&lon={LON}&appid={api_key}&units={UNITS}&lang={LANG}&cnt=8"
    )

    cur  = requests.get(current_url,  timeout=10).json()
    fore = requests.get(forecast_url, timeout=10).json()

    today_temps = [item["main"]["temp"] for item in fore.get("list", [])]
    feels_like  = cur["main"].get("feels_like", cur["main"]["temp"])
    humidity    = cur["main"].get("humidity", 0)
    wind_speed  = cur.get("wind", {}).get("speed", 0)  # m/s
    description = cur["weather"][0]["description"].capitalize()
    main        = cur["weather"][0]["main"]
    icon        = _get_icon(main)

    # Sunrise / sunset
    sunrise = datetime.fromtimestamp(cur["sys"]["sunrise"]).strftime("%H:%M")
    sunset  = datetime.fromtimestamp(cur["sys"]["sunset"]).strftime("%H:%M")

    return {
        "city":        CITY,
        "icon":        icon,
        "temp":        round(cur["main"]["temp"]),
        "feels_like":  round(feels_like),
        "temp_min":    round(min(today_temps)) if today_temps else round(cur["main"]["temp_min"]),
        "temp_max":    round(max(today_temps)) if today_temps else round(cur["main"]["temp_max"]),
        "description": description,
        "humidity":    humidity,
        "wind_kmh":    round(wind_speed * 3.6, 1),
        "sunrise":     sunrise,
        "sunset":      sunset,
    }
