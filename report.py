"""
report.py — Generiranje HTML i plain-text verzija dnevnog izvještaja
Koristi inline Jinja2 template za HTML email.
"""

from datetime import datetime
from jinja2 import Template

DAYS_BS = ["Ponedjeljak", "Utorak", "Srijeda", "Četvrtak", "Petak", "Subota", "Nedjelja"]
MONTHS_BS = ["januara", "februara", "marta", "aprila", "maja", "juna",
             "jula", "augusta", "septembra", "oktobra", "novembra", "decembra"]

CATEGORY_META = {
    "ai":            {"label": "Umjetna Inteligencija (AI)", "color": "#6366f1", "emoji": "🤖"},
    "sarajevo":      {"label": "Sarajevo — lokalne vijesti",  "color": "#0ea5e9", "emoji": "🏙️"},
    "bih":           {"label": "Bosna i Hercegovina",         "color": "#10b981", "emoji": "🇧🇦"},
    "geopolitics":   {"label": "Geopolitika i sukobi",        "color": "#ef4444", "emoji": "🌍"},
    "astronomy":     {"label": "Astronomija",                 "color": "#8b5cf6", "emoji": "🔭"},
    "astrophotography": {"label": "Astrofotografija",         "color": "#f59e0b", "emoji": "📷"},
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="bs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dnevni izvještaj — {{ date_str }}</title>
<style>
  body { margin:0; padding:0; background:#f3f4f6; font-family: 'Segoe UI', Arial, sans-serif; }
  .wrapper { max-width:680px; margin:0 auto; padding:24px 16px; }
  .header { background:linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius:12px; padding:28px 32px; margin-bottom:20px; color:#fff; }
  .header h1 { margin:0 0 4px; font-size:22px; font-weight:600; letter-spacing:-0.3px; }
  .header p  { margin:0; font-size:13px; color:#94a3b8; }
  /* Weather card */
  .weather { background:#fff; border-radius:12px; padding:24px 28px;
             margin-bottom:20px; border:1px solid #e2e8f0; }
  .weather-top { display:flex; align-items:center; gap:16px; }
  .weather-icon { font-size:42px; line-height:1; }
  .weather-main h2 { margin:0; font-size:36px; font-weight:700; color:#1e293b; }
  .weather-main p  { margin:4px 0 0; font-size:14px; color:#64748b; }
  .weather-details { display:flex; gap:24px; margin-top:18px; flex-wrap:wrap; }
  .wd-item { font-size:13px; color:#64748b; }
  .wd-item strong { color:#1e293b; display:block; font-size:15px; margin-bottom:2px; }
  /* News section */
  .section { background:#fff; border-radius:12px; margin-bottom:16px;
             border:1px solid #e2e8f0; overflow:hidden; }
  .section-header { padding:14px 20px; display:flex; align-items:center; gap:10px;
                    border-bottom:1px solid #f1f5f9; }
  .section-header .emoji { font-size:18px; }
  .section-header h3 { margin:0; font-size:15px; font-weight:600; }
  .section-stripe { width:4px; height:100%; min-height:44px; border-radius:2px 0 0 2px; }
  .article { padding:12px 20px; border-bottom:1px solid #f8fafc; display:flex;
             flex-direction:column; gap:4px; }
  .article:last-child { border-bottom:none; }
  .article a { font-size:14px; font-weight:500; color:#1e293b; text-decoration:none; line-height:1.4; }
  .article a:hover { color:#3b82f6; }
  .article .meta { font-size:12px; color:#94a3b8; }
  .article .desc { font-size:13px; color:#64748b; line-height:1.5; margin-top:2px; }
  .no-news { padding:14px 20px; font-size:13px; color:#94a3b8; font-style:italic; }
  /* Footer */
  .footer { text-align:center; font-size:11px; color:#94a3b8; margin-top:20px; padding:8px; }
</style>
</head>
<body>
<div class="wrapper">

  <!-- Header -->
  <div class="header">
    <h1>📋 Dnevni izvještaj</h1>
    <p>{{ date_str }} &nbsp;·&nbsp; Automatski generisan u 07:30</p>
  </div>

  <!-- Vremenska prognoza -->
  <div class="weather">
    <div class="weather-top">
      <div class="weather-icon">{{ weather.icon }}</div>
      <div class="weather-main">
        <h2>{{ weather.temp }}°C</h2>
        <p>{{ weather.description }} &nbsp;·&nbsp; Osjeća se kao {{ weather.feels_like }}°C</p>
      </div>
    </div>
    <div class="weather-details">
      <div class="wd-item"><strong>{{ weather.temp_min }}° / {{ weather.temp_max }}°</strong>Min / Maks</div>
      <div class="wd-item"><strong>{{ weather.humidity }}%</strong>Vlažnost</div>
      <div class="wd-item"><strong>{{ weather.wind_kmh }} km/h</strong>Vjetar</div>
      <div class="wd-item"><strong>{{ weather.sunrise }}</strong>Izlazak sunca</div>
      <div class="wd-item"><strong>{{ weather.sunset }}</strong>Zalazak sunca</div>
    </div>
  </div>

  <!-- Vijesti po kategorijama -->
  {% for cat_key, meta in categories.items() %}
  <div class="section">
    <div class="section-header" style="border-left:4px solid {{ meta.color }};">
      <span class="emoji">{{ meta.emoji }}</span>
      <h3 style="color:{{ meta.color }};">{{ meta.label }}</h3>
    </div>
    {% if news[cat_key] %}
      {% for article in news[cat_key] %}
      <div class="article">
        <a href="{{ article.url }}" target="_blank">{{ article.title }}</a>
        <span class="meta">{{ article.source }}</span>
        {% if article.desc %}<div class="desc">{{ article.desc[:160] }}{% if article.desc|length > 160 %}…{% endif %}</div>{% endif %}
      </div>
      {% endfor %}
    {% else %}
      <div class="no-news">Nema vijesti za ovu kategoriju.</div>
    {% endif %}
  </div>
  {% endfor %}

  <div class="footer">
    Generirano automatski · Python Daily Digest · Sarajevo, BiH
  </div>
</div>
</body>
</html>"""


def _bs_date(dt: datetime) -> str:
    day_name  = DAYS_BS[dt.weekday()]
    day       = dt.day
    month     = MONTHS_BS[dt.month - 1]
    year      = dt.year
    return f"{day_name}, {day}. {month} {year}."


def build_html_report(weather: dict, news: dict) -> str:
    tmpl = Template(HTML_TEMPLATE)
    return tmpl.render(
        date_str   = _bs_date(datetime.now()),
        weather    = weather,
        news       = news,
        categories = CATEGORY_META,
    )


def build_plain_report(weather: dict, news: dict) -> str:
    """Plain-text fallback za email klijente bez HTML podrške."""
    lines = [
        f"DNEVNI IZVJEŠTAJ — {_bs_date(datetime.now())}",
        "=" * 50,
        "",
        f"VREMENSKA PROGNOZA — SARAJEVO",
        f"  {weather['icon']}  {weather['temp']}°C  ({weather['description']})",
        f"  Min/Maks: {weather['temp_min']}° / {weather['temp_max']}°",
        f"  Vlažnost: {weather['humidity']}%   Vjetar: {weather['wind_kmh']} km/h",
        f"  Izlazak: {weather['sunrise']}   Zalazak: {weather['sunset']}",
        "",
    ]
    for cat_key, meta in CATEGORY_META.items():
        lines.append(f"{meta['emoji']}  {meta['label'].upper()}")
        lines.append("-" * 40)
        articles = news.get(cat_key, [])
        if articles:
            for a in articles:
                lines.append(f"  • {a['title']}")
                lines.append(f"    ({a['source']})  {a['url']}")
        else:
            lines.append("  Nema vijesti.")
        lines.append("")
    lines.append("─" * 50)
    lines.append("Automatski generisan · Python Daily Digest")
    return "\n".join(lines)


def build_telegram_report(weather: dict, news: dict) -> str:
    """Formatiran tekst za Telegram (Markdown V2 kompatibilan)."""
    lines = [
        f"*📋 Dnevni izvještaj — {_bs_date(datetime.now())}*",
        "",
        f"*🌤 Sarajevo:* {weather['icon']} {weather['temp']}°C, {weather['description']}",
        f"Min/Maks: {weather['temp_min']}° / {weather['temp_max']}°  |  "
        f"Vlažnost: {weather['humidity']}%  |  Vjetar: {weather['wind_kmh']} km/h",
        "",
    ]
    for cat_key, meta in CATEGORY_META.items():
        lines.append(f"*{meta['emoji']} {meta['label']}*")
        articles = news.get(cat_key, [])
        if articles:
            for a in articles[:3]:  # Telegram: samo 3 po kategoriji
                title = a["title"].replace("*", "").replace("_", "").replace("[", "").replace("]", "")
                url   = a["url"]
                lines.append(f"• [{title}]({url})")
        else:
            lines.append("_Nema vijesti._")
        lines.append("")
    lines.append("_Automatski generisan u 07:30_")
    return "\n".join(lines)
