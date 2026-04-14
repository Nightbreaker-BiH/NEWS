"""
report.py — HTML izvještaj s TL;DR, astronomijom, 3-dnevnom prognozom.
"""

from datetime import datetime
from jinja2 import Template

DAYS_BS   = ["Ponedjeljak","Utorak","Srijeda","Četvrtak","Petak","Subota","Nedjelja"]
MONTHS_BS = ["januara","februara","marta","aprila","maja","juna",
             "jula","augusta","septembra","oktobra","novembra","decembra"]

CATEGORY_META = {
    "ai":               {"label": "Umjetna Inteligencija (AI)",        "color": "#6366f1", "bg": "#eef2ff", "emoji": "🤖"},
    "sarajevo":         {"label": "Sarajevo — lokalne vijesti",         "color": "#0ea5e9", "bg": "#f0f9ff", "emoji": "🏙️"},
    "bih":              {"label": "Bosna i Hercegovina",                "color": "#10b981", "bg": "#f0fdf4", "emoji": "🇧🇦"},
    "geopolitics":      {"label": "Geopolitika i sukobi u svijetu",     "color": "#ef4444", "bg": "#fef2f2", "emoji": "🌍"},
    "sport":            {"label": "Sport",                              "color": "#f97316", "bg": "#fff7ed", "emoji": "⚽"},
    "defense":          {"label": "Odbrambene tehnologije i oružje",    "color": "#64748b", "bg": "#f8fafc", "emoji": "🛡️"},
    "defense_tenders":  {"label": "Odbrambeni tenderi i nabavke",       "color": "#475569", "bg": "#f1f5f9", "emoji": "📋"},
    "science":          {"label": "Nauka — otkrića i istraživanja",     "color": "#8b5cf6", "bg": "#faf5ff", "emoji": "🔬"},
    "astronomy":        {"label": "Astronomija",                        "color": "#3b82f6", "bg": "#eff6ff", "emoji": "🔭"},
    "astrophotography": {"label": "Astrofotografija",                   "color": "#d97706", "bg": "#fffbeb", "emoji": "📷"},
    "arxiv":            {"label": "arXiv — Naučni preprinti",           "color": "#7c3aed", "bg": "#f5f3ff", "emoji": "📄"},
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="bs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ edition_label }} izvještaj — {{ date_str }}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#e2e8f0;font-family:'Segoe UI',Arial,sans-serif;padding:20px 0;}
.w{max-width:700px;margin:0 auto;padding:0 12px;}
/* HEADER */
.hdr{background:linear-gradient(135deg,#0f172a,#1e3a5f,#0f172a);border-radius:16px;
     padding:28px 32px;margin-bottom:16px;color:#fff;border:1px solid #334155;}
.hdr-row{display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:12px;}
.hdr-title{font-size:26px;font-weight:700;letter-spacing:-.5px;}
.hdr-sub{font-size:13px;color:#94a3b8;margin-top:4px;}
.hdr-badge{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
           border-radius:10px;padding:10px 16px;text-align:center;min-width:110px;}
.hdr-badge .big{font-size:22px;font-weight:700;color:#fff;display:block;}
.hdr-badge .sml{font-size:11px;color:#94a3b8;}
/* TL;DR */
.tldr{background:#fff;border-radius:14px;padding:20px 24px;margin-bottom:14px;
      border:1px solid #e2e8f0;border-left:5px solid #0f172a;}
.tldr h4{font-size:13px;font-weight:700;color:#94a3b8;text-transform:uppercase;
         letter-spacing:1px;margin-bottom:12px;}
.tldr-item{display:flex;gap:8px;align-items:flex-start;padding:5px 0;
           border-bottom:1px solid #f8fafc;font-size:13px;}
.tldr-item:last-child{border-bottom:none;}
.tldr-cat{font-weight:700;min-width:160px;color:#1e293b;flex-shrink:0;}
.tldr-text{color:#64748b;line-height:1.4;}
/* ERRORS */
.errors{background:#fef9c3;border-radius:12px;padding:14px 20px;margin-bottom:14px;
        border:1px solid #fde047;font-size:13px;color:#713f12;}
.errors strong{display:block;margin-bottom:6px;}
/* PROGNOZA */
.wx{background:#fff;border-radius:16px;padding:22px 26px;margin-bottom:14px;
    border:1px solid #e2e8f0;}
.wx-lbl{font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;
        letter-spacing:1px;margin-bottom:12px;}
.wx-top{display:flex;align-items:center;gap:18px;flex-wrap:wrap;margin-bottom:18px;}
.wx-icon{font-size:56px;line-height:1;}
.wx-temp{font-size:46px;font-weight:700;color:#0f172a;line-height:1;}
.wx-desc{font-size:14px;color:#64748b;margin-top:5px;}
.wx-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:18px;}
.wx-item{background:#f8fafc;border-radius:10px;padding:10px;text-align:center;}
.wx-item .v{font-size:15px;font-weight:700;color:#0f172a;}
.wx-item .l{font-size:10px;color:#94a3b8;margin-top:2px;text-transform:uppercase;letter-spacing:.5px;}
/* 3-day */
.forecast{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;}
.fc-day{background:#f8fafc;border-radius:10px;padding:12px;text-align:center;border:1px solid #f1f5f9;}
.fc-day .d{font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;margin-bottom:6px;}
.fc-day .i{font-size:26px;margin:4px 0;}
.fc-day .t{font-size:14px;font-weight:700;color:#0f172a;}
.fc-day .desc{font-size:11px;color:#94a3b8;margin-top:3px;}
/* ASTRO */
.astro{background:linear-gradient(135deg,#0f172a,#1e1b4b);border-radius:16px;
       padding:22px 26px;margin-bottom:14px;color:#fff;border:1px solid #312e81;}
.astro-lbl{font-size:11px;font-weight:700;color:#a5b4fc;text-transform:uppercase;
           letter-spacing:1px;margin-bottom:14px;}
.astro-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;}
.astro-box{background:rgba(255,255,255,.07);border-radius:10px;padding:14px;}
.astro-box h5{font-size:12px;color:#a5b4fc;margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px;}
.astro-val{font-size:20px;font-weight:700;color:#fff;margin-bottom:4px;}
.astro-sub{font-size:12px;color:#94a3b8;}
.planet-row{display:flex;justify-content:space-between;align-items:center;
            padding:5px 0;border-bottom:1px solid rgba(255,255,255,.08);font-size:13px;}
.planet-row:last-child{border-bottom:none;}
.planet-name{color:#e2e8f0;font-weight:600;}
.planet-info{color:#94a3b8;font-size:12px;}
.seeing-bar{display:flex;gap:3px;margin:8px 0;}
.seeing-dot{width:26px;height:8px;border-radius:4px;background:rgba(255,255,255,.15);}
.seeing-dot.on{background:#22c55e;}
.recommendation{background:rgba(255,255,255,.07);border-radius:10px;padding:12px;
                font-size:13px;color:#e2e8f0;margin-top:14px;line-height:1.5;}
/* SEKCIJE VIJESTI */
.sec{background:#fff;border-radius:14px;margin-bottom:12px;border:1px solid #e2e8f0;overflow:hidden;}
.sec-hdr{padding:14px 20px;display:flex;align-items:center;gap:10px;}
.sec-hdr .ico{font-size:20px;width:36px;height:36px;display:flex;align-items:center;
              justify-content:center;border-radius:9px;}
.sec-hdr h3{font-size:15px;font-weight:700;margin:0;flex:1;}
.sec-hdr .cnt{font-size:12px;color:#94a3b8;background:#f1f5f9;border-radius:6px;padding:3px 8px;}
.art{padding:12px 20px;border-top:1px solid #f8fafc;display:flex;gap:12px;}
.art-n{font-size:11px;font-weight:700;color:#cbd5e1;min-width:20px;padding-top:2px;}
.art a{font-size:14px;font-weight:600;color:#0f172a;text-decoration:none;
       line-height:1.4;display:block;margin-bottom:4px;}
.art a:hover{color:#3b82f6;}
.art-src{font-size:11px;color:#fff;padding:2px 7px;border-radius:4px;display:inline-block;}
.art-desc{font-size:12px;color:#64748b;line-height:1.45;margin-top:5px;}
.nonews{padding:16px 20px;font-size:13px;color:#94a3b8;font-style:italic;text-align:center;}
/* FOOTER */
.footer{text-align:center;padding:18px;background:#f8fafc;border-radius:12px;
        border:1px solid #e2e8f0;margin-top:6px;}
.footer p{font-size:12px;color:#94a3b8;line-height:1.9;}
</style>
</head>
<body>
<div class="w">

<!-- HEADER -->
<div class="hdr">
  <div class="hdr-row">
    <div>
      <div class="hdr-title">{{ edition_emoji }} {{ edition_label }} izvještaj</div>
      <div class="hdr-sub">{{ date_str }}</div>
    </div>
    <div class="hdr-badge">
      <span class="big">{{ weather.temp }}°C</span>
      <span class="sml">{{ weather.icon }} Sarajevo</span>
    </div>
  </div>
</div>

<!-- TL;DR -->
<div class="tldr">
  <h4>⚡ TL;DR — Najvažnije u jednoj rečenici</h4>
  {% for cat_key, meta in categories.items() %}
  {% set arts = news.get(cat_key, []) %}
  <div class="tldr-item">
    <span class="tldr-cat">{{ meta.emoji }} {{ meta.label[:20] }}{% if meta.label|length > 20 %}…{% endif %}</span>
    <span class="tldr-text">
      {% if arts %}{{ arts[0].title[:110] }}{% if arts[0].title|length > 110 %}…{% endif %}
      {% else %}<em>Nema novih vijesti</em>{% endif %}
    </span>
  </div>
  {% endfor %}
</div>

<!-- GREŠKE (ako postoje) -->
{% if errors %}
<div class="errors">
  <strong>⚠️ Upozorenje — kategorije bez vijesti:</strong>
  {% for e in errors %}{{ e }}{% if not loop.last %}, {% endif %}{% endfor %}<br>
  <span style="margin-top:4px;display:block;">RSS feedovi za ove kategorije su privremeno nedostupni.</span>
</div>
{% endif %}

<!-- PROGNOZA -->
<div class="wx">
  <div class="wx-lbl">☁️ Vremenska prognoza — Sarajevo</div>
  <div class="wx-top">
    <div class="wx-icon">{{ weather.icon }}</div>
    <div>
      <div class="wx-temp">{{ weather.temp }}°C</div>
      <div class="wx-desc">{{ weather.description }} · Osjeća se kao <strong>{{ weather.feels_like }}°C</strong></div>
    </div>
  </div>
  <div class="wx-grid">
    <div class="wx-item"><div class="v">{{ weather.temp_min }}° / {{ weather.temp_max }}°</div><div class="l">Min / Maks</div></div>
    <div class="wx-item"><div class="v">{{ weather.humidity }}%</div><div class="l">Vlažnost</div></div>
    <div class="wx-item"><div class="v">{{ weather.wind_kmh }} km/h</div><div class="l">Vjetar</div></div>
    <div class="wx-item"><div class="v">{{ weather.cloud_pct }}%</div><div class="l">Oblačnost</div></div>
    <div class="wx-item"><div class="v">{{ weather.sunrise }}</div><div class="l">Izlazak ☀️</div></div>
    <div class="wx-item"><div class="v">{{ weather.sunset }}</div><div class="l">Zalazak ☀️</div></div>
  </div>
  {% if weather.forecast_3day %}
  <div class="wx-lbl" style="margin-top:4px;">📅 Naredna 3 dana</div>
  <div class="forecast">
    {% for day in weather.forecast_3day %}
    <div class="fc-day">
      <div class="d">{{ day.day_name[:3] }} · {{ day.date_str }}</div>
      <div class="i">{{ day.icon }}</div>
      <div class="t">{{ day.temp_min }}° / {{ day.temp_max }}°</div>
      <div class="desc">{{ day.description[:30] }}</div>
    </div>
    {% endfor %}
  </div>
  {% endif %}
</div>

<!-- ASTRONOMSKA SEKCIJA -->
{% if astro and not astro.error %}
<div class="astro">
  <div class="astro-lbl">🌌 Astronomija Sarajevo — večeras u {{ astro.obs_time }}</div>

  <div class="astro-grid">
    <div class="astro-box">
      <h5>🌙 Faza Mjeseca</h5>
      <div class="astro-val">{{ astro.moon_phase_name }}</div>
      <div class="astro-sub">{{ astro.moon_phase_pct }}% osvjetljenosti</div>
      <div class="astro-sub" style="margin-top:6px;">Izlazak: {{ astro.moon_rise }} · Zalazak: {{ astro.moon_set }}</div>
      <div style="margin-top:8px;font-size:13px;">{{ astro.moon_emoji }} {{ astro.moon_msg }}</div>
    </div>
    <div class="astro-box">
      <h5>👁️ Atmospheric Seeing</h5>
      <div class="seeing-bar">
        {% for i in range(5) %}
        <div class="seeing-dot {% if i < astro.seeing_score %}on{% endif %}"></div>
        {% endfor %}
      </div>
      <div class="astro-val" style="font-size:16px;">{{ astro.seeing_stars }}</div>
      <div class="astro-sub">{{ astro.seeing_text }}</div>
    </div>
  </div>

  {% if astro.visible_planets %}
  <div class="astro-box" style="margin-bottom:12px;">
    <h5>✨ Vidljive planete večeras (visina > 8°)</h5>
    {% for p in astro.visible_planets %}
    <div class="planet-row">
      <span class="planet-name">{{ p.name }}</span>
      <span class="planet-info">{{ p.alt }}° visine · {{ p.compass }} · mag {{ p.mag }}</span>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if astro.not_visible %}
  <div style="font-size:12px;color:#64748b;margin-bottom:10px;">
    Nisu vidljive: {{ astro.not_visible | join(', ') }}
  </div>
  {% endif %}

  <div class="recommendation">{{ astro.recommendation }}</div>
</div>
{% endif %}

<!-- KATEGORIJE VIJESTI -->
{% for cat_key, meta in categories.items() %}
{% set arts = news.get(cat_key, []) %}
<div class="sec">
  <div class="sec-hdr" style="background:{{ meta.bg }};border-bottom:2px solid {{ meta.color }}25;">
    <div class="ico" style="background:{{ meta.color }}20;">{{ meta.emoji }}</div>
    <h3 style="color:{{ meta.color }};">{{ meta.label }}</h3>
    <span class="cnt">{{ arts|length }} vijesti</span>
  </div>
  {% if arts %}
    {% for a in arts %}
    <div class="art">
      <div class="art-n">#{{ loop.index }}</div>
      <div style="flex:1;">
        <a href="{{ a.url }}" target="_blank">{{ a.title }}</a>
        <span class="art-src" style="background:{{ meta.color }};">{{ a.source[:28] }}</span>
        {% if a.desc %}<div class="art-desc">{{ a.desc[:200] }}{% if a.desc|length > 200 %}…{% endif %}</div>{% endif %}
      </div>
    </div>
    {% endfor %}
  {% else %}
    <div class="nonews">⚠️ Nema vijesti u ovoj kategoriji.</div>
  {% endif %}
</div>
{% endfor %}

<div class="footer">
  <p>📋 <strong>{{ edition_label }} izvještaj</strong> · {{ date_str }}</p>
  <p>Sarajevo, Bosna i Hercegovina · Automatski generisan</p>
  <p style="font-size:11px;color:#cbd5e1;">
    Izvori: BBC · Reuters · Al Jazeera · NASA · TechCrunch · VentureBeat · Klix · N1 · Oslobođenje · DefenseNews · arXiv · ScienceDaily
  </p>
</div>

</div>
</body>
</html>"""


def _bs_date(dt):
    return f"{DAYS_BS[dt.weekday()]}, {dt.day}. {MONTHS_BS[dt.month-1]} {dt.year}."


def _edition_info(dt):
    if dt.hour < 12:
        return "🌅", "Jutarnji"
    return "🌆", "Večernji"


def build_html_report(weather, news, astro=None, errors=None):
    now = datetime.now()
    emoji, label = _edition_info(now)
    tmpl = Template(HTML_TEMPLATE)
    return tmpl.render(
        date_str      = _bs_date(now),
        edition_emoji = emoji,
        edition_label = label,
        weather       = weather,
        news          = news,
        astro         = astro or {},
        errors        = errors or [],
        categories    = CATEGORY_META,
    )


def build_plain_report(weather, news, astro=None, errors=None):
    now = datetime.now()
    emoji, label = _edition_info(now)
    lines = [
        "="*55,
        f"  {emoji} {label.upper()} IZVJEŠTAJ",
        f"  {_bs_date(now)}",
        "="*55, "",
        f"PROGNOZA — SARAJEVO",
        f"  {weather['icon']}  {weather['temp']}°C  ({weather['description']})",
        f"  Min/Maks: {weather['temp_min']}° / {weather['temp_max']}°",
        f"  Oblačnost: {weather['cloud_pct']}%  |  Vjetar: {weather['wind_kmh']} km/h",
        f"  Izlazak: {weather['sunrise']}  |  Zalazak: {weather['sunset']}",
        "",
    ]
    if errors:
        lines += [f"⚠️ Kategorije bez vijesti: {', '.join(errors)}", ""]

    for key, meta in CATEGORY_META.items():
        lines.append(f"{meta['emoji']}  {meta['label'].upper()}")
        lines.append("-"*45)
        for i, a in enumerate(news.get(key, []), 1):
            lines.append(f"  {i:2}. {a['title']}")
            lines.append(f"      [{a['source']}]  {a['url']}")
        if not news.get(key):
            lines.append("  Nema vijesti.")
        lines.append("")
    lines += ["="*55, "Automatski generisan | Python Daily Digest"]
    return "\n".join(lines)


def build_telegram_report(weather, news, astro=None, errors=None):
    now = datetime.now()
    emoji, label = _edition_info(now)
    lines = [
        f"*{emoji} {label} izvještaj — {_bs_date(now)}*",
        "",
        f"*🌤 Sarajevo:* {weather['icon']} {weather['temp']}°C, {weather['description']}",
        f"Min/Maks: {weather['temp_min']}°/{weather['temp_max']}°  |  Oblačnost: {weather['cloud_pct']}%",
    ]
    if astro and not astro.get('error'):
        lines += [
            "",
            f"*🌌 Astronomija večeras:* {astro.get('moon_phase_name','')} ({astro.get('moon_phase_pct',0)}%)",
            astro.get('recommendation',''),
        ]
    lines.append("")
    for key, meta in CATEGORY_META.items():
        arts = news.get(key, [])
        lines.append(f"*{meta['emoji']} {meta['label']}*")
        for a in arts[:3]:
            t = a['title'].replace('*','').replace('_','')[:100]
            lines.append(f"• [{t}]({a['url']})")
        if not arts:
            lines.append("_Nema vijesti._")
        lines.append("")
    lines.append("_Automatski generisan_")
    return "\n".join(lines)
