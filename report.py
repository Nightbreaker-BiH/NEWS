"""
report.py — Generiranje HTML izvještaja.
Lijep dizajn, 9 kategorija, 10 vijesti po kategoriji.
"""

from datetime import datetime
from jinja2 import Template

DAYS_BS   = ["Ponedjeljak","Utorak","Srijeda","Četvrtak","Petak","Subota","Nedjelja"]
MONTHS_BS = ["januara","februara","marta","aprila","maja","juna",
             "jula","augusta","septembra","oktobra","novembra","decembra"]

CATEGORY_META = {
    "ai":               {"label": "Umjetna Inteligencija (AI)",      "color": "#6366f1", "bg": "#eef2ff", "emoji": "🤖"},
    "sarajevo":         {"label": "Sarajevo — lokalne vijesti",       "color": "#0ea5e9", "bg": "#f0f9ff", "emoji": "🏙️"},
    "bih":              {"label": "Bosna i Hercegovina",              "color": "#10b981", "bg": "#f0fdf4", "emoji": "🇧🇦"},
    "geopolitics":      {"label": "Geopolitika i sukobi u svijetu",   "color": "#ef4444", "bg": "#fef2f2", "emoji": "🌍"},
    "sport":            {"label": "Sport",                            "color": "#f97316", "bg": "#fff7ed", "emoji": "⚽"},
    "defense":          {"label": "Odbrambene tehnologije i oružje",  "color": "#64748b", "bg": "#f8fafc", "emoji": "🛡️"},
    "science":          {"label": "Nauka — otkrića i istraživanja",   "color": "#8b5cf6", "bg": "#faf5ff", "emoji": "🔬"},
    "astronomy":        {"label": "Astronomija",                      "color": "#3b82f6", "bg": "#eff6ff", "emoji": "🔭"},
    "astrophotography": {"label": "Astrofotografija",                 "color": "#d97706", "bg": "#fffbeb", "emoji": "📷"},
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="bs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dnevni izvještaj — {{ date_str }}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#e2e8f0;font-family:'Segoe UI',Arial,sans-serif;padding:20px 0;}
.wrap{max-width:700px;margin:0 auto;padding:0 12px;}

/* HEADER */
.hdr{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#0f172a 100%);
     border-radius:16px;padding:30px 36px;margin-bottom:20px;color:#fff;
     border:1px solid #334155;}
.hdr-top{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;}
.hdr-title{font-size:26px;font-weight:700;letter-spacing:-0.5px;}
.hdr-sub{font-size:13px;color:#94a3b8;margin-top:4px;}
.hdr-badge{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);
           border-radius:8px;padding:8px 14px;font-size:12px;color:#cbd5e1;text-align:center;}
.hdr-badge strong{display:block;font-size:18px;color:#fff;}

/* PROGNOZA */
.wx{background:#fff;border-radius:16px;padding:24px 28px;margin-bottom:16px;
    border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,.06);}
.wx-row{display:flex;align-items:center;gap:20px;flex-wrap:wrap;}
.wx-icon{font-size:60px;line-height:1;}
.wx-main{}
.wx-temp{font-size:48px;font-weight:700;color:#0f172a;line-height:1;}
.wx-desc{font-size:14px;color:#64748b;margin-top:6px;}
.wx-city{font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;}
.wx-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:18px;}
.wx-item{background:#f8fafc;border-radius:10px;padding:12px;text-align:center;border:1px solid #f1f5f9;}
.wx-item .val{font-size:17px;font-weight:700;color:#0f172a;}
.wx-item .lbl{font-size:11px;color:#94a3b8;margin-top:2px;text-transform:uppercase;letter-spacing:.5px;}

/* SEKCIJE */
.sec{background:#fff;border-radius:16px;margin-bottom:14px;
     border:1px solid #e2e8f0;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.05);}
.sec-hdr{padding:16px 22px;display:flex;align-items:center;gap:12px;}
.sec-hdr .ico{font-size:22px;width:38px;height:38px;display:flex;align-items:center;
              justify-content:center;border-radius:10px;}
.sec-hdr h3{font-size:15px;font-weight:700;margin:0;}
.sec-hdr .cnt{margin-left:auto;font-size:12px;color:#94a3b8;background:#f1f5f9;
              border-radius:6px;padding:3px 8px;}

/* VIJESTI */
.art{padding:14px 22px;border-top:1px solid #f8fafc;display:flex;gap:14px;align-items:flex-start;}
.art:first-of-type{border-top:none;}
.art-num{font-size:12px;font-weight:700;color:#cbd5e1;min-width:22px;padding-top:2px;}
.art-body{}
.art a{font-size:14px;font-weight:600;color:#0f172a;text-decoration:none;
       line-height:1.45;display:block;margin-bottom:5px;}
.art a:hover{color:#3b82f6;}
.art-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
.art-src{font-size:11px;font-weight:600;color:#fff;padding:2px 8px;border-radius:4px;}
.art-desc{font-size:13px;color:#64748b;line-height:1.5;margin-top:6px;}

/* NO NEWS */
.no-news{padding:18px 22px;font-size:13px;color:#94a3b8;font-style:italic;text-align:center;}

/* DIVIDER */
.divider{height:1px;background:linear-gradient(90deg,transparent,#e2e8f0,transparent);
         margin:4px 0;}

/* FOOTER */
.footer{text-align:center;padding:20px;background:#f8fafc;border-radius:12px;
        border:1px solid #e2e8f0;margin-top:8px;}
.footer p{font-size:12px;color:#94a3b8;line-height:1.8;}
</style>
</head>
<body>
<div class="wrap">

<!-- HEADER -->
<div class="hdr">
  <div class="hdr-top">
    <div>
      <div class="hdr-title">📋 Dnevni izvještaj</div>
      <div class="hdr-sub">{{ date_str }} &nbsp;·&nbsp; Automatski generisan</div>
    </div>
    <div class="hdr-badge">
      <strong>{{ edition }}</strong>
      Sarajevo, BiH
    </div>
  </div>
</div>

<!-- PROGNOZA -->
<div class="wx">
  <div class="wx-city">☁️ Vremenska prognoza — Sarajevo</div>
  <div class="wx-row">
    <div class="wx-icon">{{ weather.icon }}</div>
    <div class="wx-main">
      <div class="wx-temp">{{ weather.temp }}°C</div>
      <div class="wx-desc">{{ weather.description }} &nbsp;·&nbsp; Osjeća se kao <strong>{{ weather.feels_like }}°C</strong></div>
    </div>
  </div>
  <div class="wx-grid">
    <div class="wx-item"><div class="val">{{ weather.temp_min }}° / {{ weather.temp_max }}°</div><div class="lbl">Min / Maks</div></div>
    <div class="wx-item"><div class="val">{{ weather.humidity }}%</div><div class="lbl">Vlažnost</div></div>
    <div class="wx-item"><div class="val">{{ weather.wind_kmh }} km/h</div><div class="lbl">Vjetar</div></div>
    <div class="wx-item"><div class="val">{{ weather.sunrise }}</div><div class="lbl">Izlazak ☀️</div></div>
    <div class="wx-item"><div class="val">{{ weather.sunset }}</div><div class="lbl">Zalazak ☀️</div></div>
    <div class="wx-item"><div class="val">🌙</div><div class="lbl">Faza Mjeseca</div></div>
  </div>
</div>

<!-- KATEGORIJE -->
{% for cat_key, meta in categories.items() %}
{% set arts = news.get(cat_key, []) %}
<div class="sec">
  <div class="sec-hdr" style="background:{{ meta.bg }};border-bottom:2px solid {{ meta.color }}20;">
    <div class="ico" style="background:{{ meta.color }}20;">{{ meta.emoji }}</div>
    <h3 style="color:{{ meta.color }};">{{ meta.label }}</h3>
    <span class="cnt">{{ arts|length }} vijesti</span>
  </div>
  {% if arts %}
    {% for article in arts %}
    <div class="art">
      <div class="art-num">#{{ loop.index }}</div>
      <div class="art-body">
        <a href="{{ article.url }}" target="_blank">{{ article.title }}</a>
        <div class="art-meta">
          <span class="art-src" style="background:{{ meta.color }};">{{ article.source[:30] }}</span>
        </div>
        {% if article.desc %}
        <div class="art-desc">{{ article.desc[:200] }}{% if article.desc|length > 200 %}…{% endif %}</div>
        {% endif %}
      </div>
    </div>
    {% if not loop.last %}<div class="divider"></div>{% endif %}
    {% endfor %}
  {% else %}
    <div class="no-news">⚠️ Nema vijesti za ovu kategoriju.</div>
  {% endif %}
</div>
{% endfor %}

<div class="footer">
  <p>📋 <strong>Dnevni izvještaj</strong> — automatski generisan putem Python skripte</p>
  <p>Sarajevo, Bosna i Hercegovina &nbsp;·&nbsp; {{ date_str }}</p>
  <p style="margin-top:6px;font-size:11px;color:#cbd5e1;">
    Vijesti: BBC, Reuters, Al Jazeera, Klix.ba, N1, Oslobođenje, NASA, TechCrunch, VentureBeat, DefenseNews...
  </p>
</div>

</div>
</body>
</html>"""


def _bs_date(dt):
    return f"{DAYS_BS[dt.weekday()]}, {dt.day}. {MONTHS_BS[dt.month-1]} {dt.year}."


def _edition(dt):
    return "🌅 Jutarnje" if dt.hour < 12 else "🌆 Večernje"


def build_html_report(weather, news):
    tmpl = Template(HTML_TEMPLATE)
    now  = datetime.now()
    return tmpl.render(
        date_str   = _bs_date(now),
        edition    = _edition(now),
        weather    = weather,
        news       = news,
        categories = CATEGORY_META,
    )


def build_plain_report(weather, news):
    now   = datetime.now()
    lines = [
        f"{'='*55}",
        f"  DNEVNI IZVJEŠTAJ — {_edition(now)}",
        f"  {_bs_date(now)}",
        f"{'='*55}",
        "",
        f"PROGNOZA — SARAJEVO",
        f"  {weather['icon']}  {weather['temp']}°C  ({weather['description']})",
        f"  Min/Maks: {weather['temp_min']}° / {weather['temp_max']}°",
        f"  Vlažnost: {weather['humidity']}%  |  Vjetar: {weather['wind_kmh']} km/h",
        f"  Izlazak: {weather['sunrise']}  |  Zalazak: {weather['sunset']}",
        "",
    ]
    for key, meta in CATEGORY_META.items():
        lines.append(f"{meta['emoji']}  {meta['label'].upper()}")
        lines.append("-" * 45)
        for i, a in enumerate(news.get(key, []), 1):
            lines.append(f"  {i:2}. {a['title']}")
            lines.append(f"      [{a['source']}]  {a['url']}")
        if not news.get(key):
            lines.append("  Nema vijesti.")
        lines.append("")
    lines.append(f"{'='*55}")
    lines.append("Automatski generisan | Python Daily Digest")
    return "\n".join(lines)


def build_telegram_report(weather, news):
    now   = datetime.now()
    lines = [
        f"*📋 {_edition(now)} izvještaj — {_bs_date(now)}*",
        "",
        f"*🌤 Sarajevo:* {weather['icon']} {weather['temp']}°C, {weather['description']}",
        f"Min/Maks: {weather['temp_min']}°/{weather['temp_max']}°  |  Vlažnost: {weather['humidity']}%",
        "",
    ]
    for key, meta in CATEGORY_META.items():
        arts = news.get(key, [])
        lines.append(f"*{meta['emoji']} {meta['label']}*")
        for a in arts[:3]:
            t = a['title'].replace('*','').replace('_','').replace('[','').replace(']','')[:100]
            lines.append(f"• [{t}]({a['url']})")
        if not arts:
            lines.append("_Nema vijesti._")
        lines.append("")
    lines.append("_Automatski generisan_")
    return "\n".join(lines)
