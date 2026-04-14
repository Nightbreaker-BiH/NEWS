"""
news.py — Vijesti putem RSS, 11 kategorija, 10 članaka svaka.
Uključuje arXiv, odbrambene nabavke, filtriranje duplikata.
"""

import re
import logging
import feedparser
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)
MAX_ARTICLES = 10

# ── Feedovi po kategoriji ──────────────────────────────────────────────
RSS = {
    "ai": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://venturebeat.com/category/ai/feed/",
        "https://www.artificialintelligence-news.com/feed/",
        "https://www.technologyreview.com/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://openai.com/blog/rss/",
    ],
    "sarajevo": [
        "https://www.klix.ba/rss/vijesti/sarajevo",
        "https://www.klix.ba/rss/vijesti",
        "https://www.avaz.ba/rss",
        "https://www.oslobodjenje.ba/rss",
        "https://ba.n1info.com/feed/",
        "https://www.radiosarajevo.ba/rss",
        "https://www.slobodna-bosna.ba/rss",
    ],
    "bih": [
        "https://www.klix.ba/rss/vijesti/bih",
        "https://ba.n1info.com/feed/",
        "https://www.oslobodjenje.ba/rss",
        "https://www.avaz.ba/rss",
        "https://www.slobodna-bosna.ba/rss",
        "https://www.radiosarajevo.ba/rss",
    ],
    "geopolitics": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://rss.dw.com/rdf/rss-en-world",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://feeds.skynews.com/feeds/rss/world.xml",
        "https://foreignpolicy.com/feed/",
    ],
    "sport": [
        "https://www.klix.ba/rss/sport",
        "https://www.avaz.ba/rss/sport",
        "https://www.oslobodjenje.ba/rss/sport",
        "http://feeds.bbci.co.uk/sport/rss.xml",
        "https://feeds.reuters.com/reuters/sportsNews",
        "https://www.eurosport.com/rss/",
    ],
    "defense": [
        "https://www.defensenews.com/arc/outboundfeeds/rss/",
        "https://breakingdefense.com/feed/",
        "https://www.defenseone.com/rss/all/",
        "https://taskandpurpose.com/feed/",
        "https://www.popularmechanics.com/rss/all.xml/",
        "https://www.janes.com/feeds/news",
    ],
    "defense_tenders": [
        "https://www.nato.int/cps/en/natolive/news.rss",
        "https://www.sipri.org/news/feed",
        "https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=945&max=10",
        "https://www.gov.uk/government/organisations/ministry-of-defence.atom",
        "https://feeds.reuters.com/reuters/worldNews",
    ],
    "science": [
        "https://www.sciencedaily.com/rss/all.xml",
        "https://phys.org/rss-feed/",
        "https://www.newscientist.com/feed/home/",
        "https://feeds.nature.com/nature/rss/current",
        "https://www.livescience.com/feeds/all",
        "https://www.sciencemag.org/rss/news_current.xml",
    ],
    "astronomy": [
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "https://www.space.com/feeds/all",
        "https://www.universetoday.com/feed/",
        "https://skyandtelescope.org/feed/",
        "https://phys.org/rss-feed/space-news/",
        "https://www.astronomy.com/feed/",
    ],
    "astrophotography": [
        "https://apod.nasa.gov/apod.rss",
        "https://astrobackyard.com/feed/",
        "https://www.space.com/feeds/all",
        "https://skyandtelescope.org/feed/",
        "https://www.digitalcameraworld.com/feeds/category/astrophotography",
    ],
    "arxiv": [
        "https://rss.arxiv.org/rss/cs.AI",
        "https://rss.arxiv.org/rss/astro-ph.IM",
        "https://rss.arxiv.org/rss/astro-ph",
        "https://rss.arxiv.org/rss/physics.optics",
        "https://rss.arxiv.org/rss/physics.ins-det",
    ],
}

# ── Filteri ────────────────────────────────────────────────────────────
BAD_WORDS = [
    "pypi", "package release", "version 0.", "npm package",
    "casino", "gambling", "nft drop", "forex signal",
    "bitcoin price prediction", "stock tip",
]

AI_KW = [
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "chatgpt", "openai", "anthropic", "claude",
    "gemini", "llm", "large language", "generative ai", "gpt",
    "ai model", "ai agent", "ai system", "ai chip", "nvidia ai",
    "google ai", "meta ai", "microsoft ai", "copilot", "midjourney",
    "robotics", "autonomous", "transformer model",
]

DEFENSE_KW = [
    "weapon", "missile", "drone", "military", "defense", "defence",
    "navy", "air force", "army", "tank", "fighter", "warship",
    "hypersonic", "stealth", "radar", "artillery", "combat",
    "warfare", "nato", "pentagon", "arms", "ballistic", "submarine",
    "aircraft carrier", "cyber attack", "autonomous weapon",
    "laser weapon", "directed energy", "procurement", "contract awarded",
]

TENDER_KW = [
    "procurement", "contract", "awarded", "tender", "acquisition",
    "purchase", "budget", "defence spending", "defense spending",
    "arms deal", "weapons deal", "military contract", "nato funding",
    "defence contract", "mil contract",
]

SCIENCE_KW = [
    "discover", "research", "scientists", "breakthrough", "experiment",
    "findings", "journal", "published", "new species", "quantum",
    "genome", "dna", "climate", "physics", "chemistry", "biology",
    "medicine", "vaccine", "technology", "innovation", "telescope",
    "particle", "fusion", "battery", "material", "study shows",
    "first time", "researchers found",
]


def _clean(text):
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", str(text)).strip()[:280]


def _is_bad(title):
    t = title.lower()
    return any(kw in t for kw in BAD_WORDS)


def _has(title, desc, keywords):
    text = (title + " " + desc).lower()
    return any(kw in text for kw in keywords)


def _get_pub_time(entry):
    """Pokušava dohvatiti datum objave članka."""
    try:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            import time
            return datetime.fromtimestamp(
                time.mktime(entry.published_parsed),
                tz=timezone.utc
            )
    except Exception:
        pass
    return None


def _is_new_for_evening(entry):
    """
    Za večernje izdanje (17:30 UTC = 19:30 CEST):
    Prikaži samo članke objavljene danas nakon 11:00 UTC (13:00 Sarajevo).
    """
    now_utc  = datetime.now(timezone.utc)
    hour_utc = now_utc.hour

    # Jutarnje izdanje (5:30 UTC) — sve iz zadnjih 24h
    if hour_utc < 12:
        return True

    # Večernje izdanje — samo novi (nakon 11:00 UTC danas)
    cutoff = now_utc.replace(hour=11, minute=0, second=0, microsecond=0)
    pub_time = _get_pub_time(entry)

    if pub_time is None:
        return True  # Ako nema datuma, uključi svejedno
    return pub_time >= cutoff


def _fetch(urls, max_n=MAX_ARTICLES, require_fn=None,
           evening_dedup=False, seen_ext=None):
    """
    Dohvata članke iz liste URL-ova s automatskim fallback-om.
    Ako jedan feed ne radi, automatski prelazi na sljedeći.
    """
    results = []
    seen    = set(seen_ext) if seen_ext else set()

    for url in urls:
        if len(results) >= max_n:
            break
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                logger.debug(f"Prazan feed: {url}")
                continue

            for entry in feed.entries:
                if len(results) >= max_n:
                    break

                title = entry.get("title", "").strip()
                if not title or title in seen or _is_bad(title):
                    continue

                # Filtriranje duplikata za večernje izdanje
                if evening_dedup and not _is_new_for_evening(entry):
                    continue

                desc = _clean(entry.get("summary") or entry.get("description") or "")

                if require_fn and not require_fn(title, desc):
                    continue

                seen.add(title)
                results.append({
                    "title":  title,
                    "source": feed.feed.get("title", "Izvor"),
                    "url":    entry.get("link", ""),
                    "desc":   desc,
                })

        except Exception as e:
            logger.warning(f"RSS greška ({url}): {e}")
            # Fallback — nastavi s narednim feedom automatski
            continue

    return results


def fetch_all_news():
    """Dohvata vijesti iz svih kategorija."""
    # Određuje li je večernje ili jutarnje izdanje
    now_utc    = datetime.now(timezone.utc)
    is_evening = now_utc.hour >= 12

    results = {}

    results["ai"] = _fetch(
        RSS["ai"],
        require_fn=lambda t, d: _has(t, d, AI_KW),
        evening_dedup=is_evening
    )
    results["sarajevo"] = _fetch(
        RSS["sarajevo"],
        evening_dedup=is_evening
    )
    results["bih"] = _fetch(
        RSS["bih"],
        evening_dedup=is_evening
    )
    results["geopolitics"] = _fetch(
        RSS["geopolitics"],
        evening_dedup=is_evening
    )
    results["sport"] = _fetch(
        RSS["sport"],
        evening_dedup=is_evening
    )
    results["defense"] = _fetch(
        RSS["defense"],
        require_fn=lambda t, d: _has(t, d, DEFENSE_KW),
        evening_dedup=is_evening
    )
    results["defense_tenders"] = _fetch(
        RSS["defense_tenders"],
        require_fn=lambda t, d: _has(t, d, TENDER_KW + DEFENSE_KW),
        evening_dedup=is_evening
    )
    results["science"] = _fetch(
        RSS["science"],
        require_fn=lambda t, d: _has(t, d, SCIENCE_KW),
        evening_dedup=is_evening
    )
    results["astronomy"] = _fetch(
        RSS["astronomy"],
        evening_dedup=is_evening
    )
    results["astrophotography"] = _fetch(
        RSS["astrophotography"],
        evening_dedup=is_evening
    )
    results["arxiv"] = _fetch(
        RSS["arxiv"]
    )

    # Log
    for k, v in results.items():
        logger.info(f"  {k:20s}: {len(v):2d} članaka")

    return results
