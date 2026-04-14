"""
news.py — Dohvatanje vijesti putem RSS feedova.
10 vijesti po kategoriji, 9 kategorija ukupno.
"""

import re
import logging
import feedparser

logger = logging.getLogger(__name__)
MAX_ARTICLES = 10

RSS_SOURCES = {
    "ai": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.artificialintelligence-news.com/feed/",
        "https://www.technologyreview.com/feed/",
        "https://venturebeat.com/category/ai/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://feeds.feedburner.com/venturebeat/SZYF",
        "https://openai.com/blog/rss/",
    ],
    "sarajevo": [
        "https://www.klix.ba/rss/vijesti/sarajevo",
        "https://www.klix.ba/rss/vijesti",
        "https://www.radiosarajevo.ba/rss",
        "https://www.oslobodjenje.ba/rss",
        "https://www.avaz.ba/rss",
        "https://ba.n1info.com/feed/",
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
    "sport": [
        "https://www.klix.ba/rss/sport",
        "https://www.oslobodjenje.ba/rss/sport",
        "https://www.avaz.ba/rss/sport",
        "http://feeds.bbci.co.uk/sport/rss.xml",
        "https://feeds.reuters.com/reuters/sportsNews",
        "https://www.eurosport.com/rss/",
        "https://ba.n1info.com/feed/",
    ],
    "defense": [
        "https://www.defensenews.com/arc/outboundfeeds/rss/",
        "https://www.janes.com/feeds/news",
        "https://www.military.com/rss-feeds/content",
        "https://breakingdefense.com/feed/",
        "https://www.defenseone.com/rss/all/",
        "https://taskandpurpose.com/feed/",
        "https://www.popularmechanics.com/rss/all.xml/",
    ],
    "science": [
        "https://www.sciencedaily.com/rss/all.xml",
        "https://phys.org/rss-feed/",
        "https://www.newscientist.com/feed/home/",
        "https://feeds.nature.com/nature/rss/current",
        "https://www.sciencemag.org/rss/news_current.xml",
        "https://www.livescience.com/feeds/all",
    ],
}

FILTER_OUT = [
    "pypi", "package release", "version 0.", "npm package",
    "casino", "gambling", "bet365", "bitcoin price",
    "nft drop", "forex signal", "stock tip", "advertisement",
]

AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "chatgpt", "openai", "anthropic", "claude",
    "gemini", "llm", "large language model", "generative ai", "gpt",
    "ai model", "robotics", "nvidia ai", "google ai", "meta ai",
    "microsoft ai", "ai research", "ai tool", "ai agent", "ai system",
    "ai chip", "ai startup", "copilot", "midjourney", "stable diffusion",
]

DEFENSE_KEYWORDS = [
    "weapon", "missile", "drone", "military", "defense", "defence",
    "navy", "air force", "army", "tank", "fighter jet", "warship",
    "hypersonic", "stealth", "radar", "ammunition", "artillery",
    "combat", "warfare", "nato", "pentagon", "arms", "ballistic",
    "submarine", "aircraft carrier", "satellite", "cyber attack",
    "autonomous weapon", "laser weapon", "directed energy",
]

SCIENCE_KEYWORDS = [
    "discover", "research", "study", "scientists", "breakthrough",
    "experiment", "findings", "journal", "published", "new species",
    "quantum", "genome", "dna", "climate", "physics", "chemistry",
    "biology", "medicine", "vaccine", "technology", "innovation",
    "telescope", "particle", "fusion", "battery", "material",
]


def _clean_html(text):
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", str(text)).strip()[:250]


def _is_bad(title):
    t = title.lower()
    return any(kw in t for kw in FILTER_OUT)


def _has_keywords(title, desc, keywords):
    text = (title + " " + desc).lower()
    return any(kw in text for kw in keywords)


def _fetch(urls, max_n=MAX_ARTICLES, require_fn=None):
    results = []
    seen = set()

    for url in urls:
        if len(results) >= max_n:
            break
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                continue
            for entry in feed.entries:
                if len(results) >= max_n:
                    break
                title = entry.get("title", "").strip()
                if not title or title in seen or _is_bad(title):
                    continue
                desc = _clean_html(
                    entry.get("summary") or entry.get("description") or ""
                )
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

    return results


def fetch_all_news():
    results = {}

    results["ai"] = _fetch(
        RSS_SOURCES["ai"],
        require_fn=lambda t, d: _has_keywords(t, d, AI_KEYWORDS)
    )
    results["sarajevo"]       = _fetch(RSS_SOURCES["sarajevo"])
    results["bih"]            = _fetch(RSS_SOURCES["bih"])
    results["geopolitics"]    = _fetch(RSS_SOURCES["geopolitics"])
    results["astronomy"]      = _fetch(RSS_SOURCES["astronomy"])
    results["astrophotography"] = _fetch(RSS_SOURCES["astrophotography"])
    results["sport"]          = _fetch(RSS_SOURCES["sport"])
    results["defense"]        = _fetch(
        RSS_SOURCES["defense"],
        require_fn=lambda t, d: _has_keywords(t, d, DEFENSE_KEYWORDS)
    )
    results["science"]        = _fetch(
        RSS_SOURCES["science"],
        require_fn=lambda t, d: _has_keywords(t, d, SCIENCE_KEYWORDS)
    )

    for k, v in results.items():
        logger.info(f"  {k}: {len(v)} članaka")

    return results
