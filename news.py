"""
news.py — Dohvatanje vijesti isključivo putem RSS feedova.
Bez NewsAPI-ja — pouzdaniji izvori, bolje filtrirane vijesti.
"""

import logging
import feedparser

logger = logging.getLogger(__name__)

MAX_ARTICLES = 5

RSS_SOURCES = {
    "ai": [
        "https://feeds.feedburner.com/venturebeat/SZYF",        # VentureBeat AI
        "https://www.artificialintelligence-news.com/feed/",     # AI News
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.technologyreview.com/feed/",                # MIT Tech Review
        "https://openai.com/blog/rss/",                         # OpenAI Blog
    ],
    "sarajevo": [
        "https://www.klix.ba/rss/vijesti/sarajevo",
        "https://radiosarajevo.ba/feed",
        "https://www.oslobodjenje.ba/rss",
    ],
    "bih": [
        "https://www.klix.ba/rss/vijesti/bih",
        "https://ba.n1info.com/feed/",
        "https://www.oslobodjenje.ba/rss",
        "https://radiosarajevo.ba/feed",
    ],
    "geopolitics": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",            # BBC World
        "https://feeds.reuters.com/reuters/worldNews",           # Reuters World
        "https://rss.dw.com/rdf/rss-en-world",                  # Deutsche Welle
        "https://www.aljazeera.com/xml/rss/all.xml",            # Al Jazeera
    ],
    "astronomy": [
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",        # NASA
        "https://www.space.com/feeds/all",                       # Space.com
        "https://www.universetoday.com/feed/",                   # Universe Today
        "https://skyandtelescope.org/feed/",                     # Sky & Telescope
    ],
    "astrophotography": [
        "https://apod.nasa.gov/apod.rss",                        # NASA APOD
        "https://astrobackyard.com/feed/",                       # AstroBackyard
        "https://www.skyatnightmagazine.com/feeds/all",          # Sky at Night
        "https://www.space.com/feeds/all",                       # Space.com
    ],
}

# Ključne riječi za filtriranje loših rezultata
FILTER_OUT = [
    "pypi", "package", "release 0.", "version 0.", "npm",
    "casino", "gambling", "bet", "crypto", "bitcoin", "nft",
    "forex", "stock tip", "price prediction",
]

# Ključne riječi koje MORAJU biti u AI vijestima
AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "chatgpt", "openai", "anthropic", "claude",
    "gemini", "llm", "large language", "generative ai", "gpt",
    "ai model", "robot", "automation", "nvidia ai", "google ai",
    "meta ai", "microsoft ai", "ai research", "ai tool",
    "ai agent", "ai system", "ai chip", "ai startup",
]


def _is_relevant_ai(title: str, desc: str) -> bool:
    text = (title + " " + desc).lower()
    has_ai = any(kw in text for kw in AI_KEYWORDS)
    has_bad = any(kw in text for kw in FILTER_OUT)
    return has_ai and not has_bad


def _is_clean(title: str) -> bool:
    title_lower = title.lower()
    return not any(kw in title_lower for kw in FILTER_OUT)


def _fetch_rss(urls: list, max_items: int = MAX_ARTICLES,
               filter_fn=None) -> list:
    articles = []
    seen = set()

    for url in urls:
        if len(articles) >= max_items:
            break
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                if not title or title in seen:
                    continue

                desc = entry.get("summary", "")
                if isinstance(desc, str):
                    # Ukloni HTML tagove iz opisa
                    import re
                    desc = re.sub(r"<[^>]+>", "", desc)[:200]

                if filter_fn and not filter_fn(title, desc):
                    continue

                if not _is_clean(title):
                    continue

                seen.add(title)
                articles.append({
                    "title":  title,
                    "source": feed.feed.get("title", url),
                    "url":    entry.get("link", ""),
                    "desc":   desc,
                })

                if len(articles) >= max_items:
                    break

        except Exception as e:
            logger.warning(f"RSS greška ({url}): {e}")

    return articles


def fetch_all_news() -> dict:
    results = {}

    # AI — sa strogim filterom
    results["ai"] = _fetch_rss(
        RSS_SOURCES["ai"],
        filter_fn=_is_relevant_ai
    )
    logger.info(f"  AI: {len(results['ai'])} članaka")

    # Sarajevo lokalne
    results["sarajevo"] = _fetch_rss(RSS_SOURCES["sarajevo"])
    logger.info(f"  Sarajevo: {len(results['sarajevo'])} članaka")

    # BiH nacionalne
    results["bih"] = _fetch_rss(RSS_SOURCES["bih"])
    logger.info(f"  BiH: {len(results['bih'])} članaka")

    # Geopolitika
    results["geopolitics"] = _fetch_rss(RSS_SOURCES["geopolitics"])
    logger.info(f"  Geopolitika: {len(results['geopolitics'])} članaka")

    # Astronomija
    results["astronomy"] = _fetch_rss(RSS_SOURCES["astronomy"])
    logger.info(f"  Astronomija: {len(results['astronomy'])} članaka")

    # Astrofotografija
    results["astrophotography"] = _fetch_rss(RSS_SOURCES["astrophotography"])
    logger.info(f"  Astrofotografija: {len(results['astrophotography'])} članaka")

    return results
