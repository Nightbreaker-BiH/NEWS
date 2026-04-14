"""
astro_local.py — Lokalni astronomski podaci za Sarajevo.
Koristi ephem biblioteku za precizne izračune.
"""

import math
import logging
from datetime import datetime, timedelta
import pytz
import ephem

logger = logging.getLogger(__name__)

LAT  = '43.8563'
LON  = '18.4131'
ELEV = 511  # metara n.m.
TZ   = pytz.timezone('Europe/Sarajevo')

PLANET_NAMES = {
    'Merkur': ephem.Mercury,
    'Venera': ephem.Venus,
    'Mars':   ephem.Mars,
    'Jupiter': ephem.Jupiter,
    'Saturn': ephem.Saturn,
    'Uran':   ephem.Uranus,
    'Neptun': ephem.Neptune,
}

PLANET_EMOJI = {
    'Merkur': '☿', 'Venera': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Uran': '⛢', 'Neptun': '♆',
}


def _observer(local_dt):
    """Kreira posmatrača za Sarajevo u datom lokalnom vremenu."""
    obs = ephem.Observer()
    obs.lat       = LAT
    obs.lon       = LON
    obs.elevation = ELEV
    obs.pressure  = 1013
    obs.horizon   = '-0:34'
    utc_dt = local_dt.astimezone(pytz.utc)
    obs.date = utc_dt.strftime('%Y/%m/%d %H:%M:%S')
    return obs


def _az_to_compass(az_deg):
    dirs = ['S','SSI','SI','ISI','I','IJI','JI','JJI',
            'J','JJZ','JZ','ZJZ','Z','ZSZ','SZ','SSZ']
    return dirs[round(az_deg / 22.5) % 16]


def _moon_phase_name(pct):
    if pct < 3:    return "🌑 Mlađak"
    elif pct < 22: return "🌒 Rastući srp"
    elif pct < 48: return "🌓 Prva četvrt"
    elif pct < 52: return "🌕 Pun Mjesec"
    elif pct < 78: return "🌖 Opadajući gibbus"
    elif pct < 92: return "🌗 Zadnja četvrt"
    elif pct < 98: return "🌘 Opadajući srp"
    else:          return "🌑 Mlađak"


def _moon_photo_rating(pct):
    if pct < 20:   return ("🟢", "Odlično za astrofoto — tamno nebo")
    elif pct < 40: return ("🟡", "Prihvatljivo — Mjesec ne smeta previše")
    elif pct < 70: return ("🟠", "Umjereno — Mjesec otežava snimanje")
    else:          return ("🔴", "Loše za astrofoto — Mjesec osvjetljava nebo")


def _seeing_from_weather(cloud_pct, wind_ms, humidity):
    score = 5
    if cloud_pct > 80:   score -= 3
    elif cloud_pct > 50: score -= 2
    elif cloud_pct > 20: score -= 1
    if wind_ms > 10:     score -= 2
    elif wind_ms > 6:    score -= 1
    if humidity > 90:    score -= 1
    return max(1, min(5, score))


def _seeing_label(score):
    return {
        5: ("⭐⭐⭐⭐⭐", "Izvanredno — idealna noć za snimanje"),
        4: ("⭐⭐⭐⭐",   "Dobro — preporučuje se snimanje"),
        3: ("⭐⭐⭐",     "Prihvatljivo — uvjetno za snimanje"),
        2: ("⭐⭐",       "Loše — kratke ekspozicije jedino moguće"),
        1: ("⭐",         "Veoma loše — snimanje se ne preporučuje"),
    }.get(score, ("?", "Nepoznato"))


def get_astro_data(weather_data=None):
    """
    Vraća rječnik s astronomskim podacima za večeras (22:00 lokalno).
    Opciono prima weather_data za seeing procjenu.
    """
    try:
        now_local = datetime.now(TZ)
        tonight   = now_local.replace(hour=22, minute=0, second=0, microsecond=0)
        obs       = _observer(tonight)

        # ── Mjesec ──────────────────────────────────────────────
        moon = ephem.Moon(obs)
        phase_pct  = round(moon.moon_phase * 100, 1)
        phase_name = _moon_phase_name(phase_pct)
        moon_emoji, moon_msg = _moon_photo_rating(phase_pct)

        try:
            obs_rise = _observer(now_local)
            moon_rise_utc = obs_rise.next_rising(ephem.Moon())
            moon_set_utc  = obs_rise.next_setting(ephem.Moon())
            moon_rise_local = ephem.Date(moon_rise_utc).datetime().replace(
                tzinfo=pytz.utc).astimezone(TZ).strftime('%H:%M')
            moon_set_local  = ephem.Date(moon_set_utc).datetime().replace(
                tzinfo=pytz.utc).astimezone(TZ).strftime('%H:%M')
        except Exception:
            moon_rise_local = "N/A"
            moon_set_local  = "N/A"

        # ── Planete ─────────────────────────────────────────────
        visible     = []
        not_visible = []

        for name, PlanetClass in PLANET_NAMES.items():
            planet = PlanetClass(obs)
            alt_deg = float(planet.alt) * 180 / math.pi
            az_deg  = float(planet.az)  * 180 / math.pi
            mag     = round(planet.mag, 1)
            emoji   = PLANET_EMOJI.get(name, '')

            if alt_deg > 8:
                visible.append({
                    'name':    f"{emoji} {name}",
                    'alt':     round(alt_deg, 0),
                    'compass': _az_to_compass(az_deg),
                    'mag':     mag,
                })
            else:
                not_visible.append(f"{emoji} {name}")

        # Sortiraj po visini — vidljiviji na vrhu
        visible.sort(key=lambda x: x['alt'], reverse=True)

        # ── Seeing ──────────────────────────────────────────────
        if weather_data:
            cloud_pct = weather_data.get('cloud_pct', 100)
            wind_ms   = weather_data.get('wind_kmh', 20) / 3.6
            humidity  = weather_data.get('humidity', 80)
            seeing_score = _seeing_from_weather(cloud_pct, wind_ms, humidity)
        else:
            seeing_score = 3

        seeing_stars, seeing_text = _seeing_label(seeing_score)

        # ── Preporuka ────────────────────────────────────────────
        if seeing_score >= 4 and phase_pct < 35:
            recommendation = "🟢 ODLIČNA NOĆ — preporučuje se izlazak na posmatranje!"
        elif seeing_score >= 3 and phase_pct < 55:
            recommendation = "🟡 DOBRA NOĆ — vrijedi pokušati, posebno planete."
        elif phase_pct > 65:
            recommendation = "🔴 Pun Mjesec otežava dubokonebno snimanje — fokusirajte se na planete."
        else:
            recommendation = "🔴 Loši atmosferski uvjeti — odgodite snimanje."

        return {
            'error':           None,
            'obs_time':        tonight.strftime('%d.%m.%Y u %H:%M'),
            'moon_phase_pct':  phase_pct,
            'moon_phase_name': phase_name,
            'moon_emoji':      moon_emoji,
            'moon_msg':        moon_msg,
            'moon_rise':       moon_rise_local,
            'moon_set':        moon_set_local,
            'visible_planets': visible,
            'not_visible':     not_visible,
            'seeing_score':    seeing_score,
            'seeing_stars':    seeing_stars,
            'seeing_text':     seeing_text,
            'recommendation':  recommendation,
        }

    except Exception as e:
        logger.error(f"Greška u astro izračunu: {e}")
        return {'error': str(e), 'visible_planets': [], 'not_visible': []}
