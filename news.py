"""
news.py — Dohvatanje vijesti putem RSS feedova.
"""

import re
import logging
import feedparser

logger = logging.getLogger(__name__)
MAX_ARTICLES = 5

RSS_SOURCES = {
    "ai": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.artificialintelligence-news.com/feed/",
        "https://www.technologyreview.com/feed/",
        "https://venturebeat.com/category/ai/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    ],
    "sarajevo": [
        "https://www.klix.ba/rss/vijesti/sarajevo",
        "https://www.klix.ba/rss/vijesti",
        "https://www.radiosarajevo.ba/rss",
        "https://www.oslobodjenje.ba/rss",
        "https://www.avaz.ba/rss",
        "https://www.slobodna-bosna.ba/rss",
        "https://ba.n1info.com/feed/",
    ],
    "bih": [
        "https://www.klix.ba/rss/vijesti/bih",
        "https://www.klix.ba/rss/vijesti",
        "https://ba.n1info.com/feed/",
        "https://www.oslobodjenje.ba/rss",
        "https://www.avaz.ba/rss",
        "https://www.slobodna-bosna.ba/rss",
        "https://www.dnevni-avaz.ba/rss",
    ],
    "geopolitics": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://rss.dw.com/rdf/rss-en-world",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://feeds.skynews.com/feeds/rss/world.xml",
    ],
    "astronomy": [
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "https://www.space.com/feeds/all",
        "https://www.universetoday.com/feed/",
        "https://skyandtelescope.org/feed/",
        "https://phys.org/rss-feed/space-news/",
    ],
    "astrophotography": [
        "https://apod.nasa.gov/apod.rss",
        "https://astrobackyard.com/feed/",
        "https://www.space.com/feeds/all",
        "https://skyandtelescope.org/feed/",
        "https://www.digitalcameraworld.com/feeds/category/astrophotography",
    ],
}

FILTER_OUT = [
    "pypi", "package release", "version 0.", "npm package",
    "casino", "gambling", "bet365", "bitcoin price",
    "nft drop", "forex signal", "stock tip",
]

AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "chatgpt", "openai", "anthropic", "claude",
    "gemini", "llm", "large language model", "generative ai", "gpt",
    "ai model", "robotics", "automation ai", "nvidia ai", "google ai",
    "meta ai", "microsoft ai", "ai research", "ai tool", "ai agent",
    "ai system", "ai chip", "ai startup", "copilot", "midjourney",
    "stable diffusion", "image generation", "text generation",
]

SARAJEVO_KEYWORDS = [
    "sarajevo", "kanton sarajevo", "grad sarajevo", "federacija",
    "bosna", "hercegovina", "bih", "fbih", "rs", "tuzla", "mostar",
    "zenica", "banja luka", "vlada", "premijer", "predsjednik",
]


def _clean_html(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()[:220]


def _is_bad(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in FILTER_OUT)


def _has_ai(title: str, desc: str) -> bool:
    text = (title + " " + desc).lower()
    return any(kw in text for kw in AI_KEYWORDS)


def _fetch(urls: list, max_n: int = MAX_ARTICLES,
           require_fn=None, seen_global: set = None) -> list:
    results = []
    seen = seen_global if seen_global is not None else set()

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
                if not title or title in seen:
                    continue
                if _is_bad(title):
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


def fetch_all_news() -> dict:
    results = {}

    results["ai"] = _fetch(
        RSS_SOURCES["ai"],
        require_fn=lambda t, d: _has_ai(t, d)
    )
    logger.info(f"  AI: {len(results['ai'])}")

    # Sarajevo — pokušaj sve feedove, prihvati šta god dođe
    seen = set()
    results["sarajevo"] = _fetch(RSS_SOURCES["sarajevo"], seen_global=seen)
    logger.info(f"  Sarajevo: {len(results['sarajevo'])}")

    # BiH — novi seen da ne duplira Sarajevo
    results["bih"] = _fetch(RSS_SOURCES["bih"])
    logger.info(f"  BiH: {len(results['bih'])}")

    results["geopolitics"] = _fetch(RSS_SOURCES["geopolitics"])
    logger.info(f"  Geopolitika: {len(results['geopolitics'])}")

    results["astronomy"] = _fetch(RSS_SOURCES["astronomy"])
    logger.info(f"  Astronomija: {len(results['astronomy'])}")

    results["astrophotography"] = _fetch(RSS_SOURCES["astrophotography"])
    logger.info(f"  Astrofotografija: {len(results['astrophotography'])}")

    return results
