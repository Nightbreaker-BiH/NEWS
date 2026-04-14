"""
news.py — Dohvatanje vijesti po kategorijama
Kombinirani pristup: NewsAPI.org + RSS feeds za lokalne izvore.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional

import requests
import feedparser

logger = logging.getLogger(__name__)

NEWS_API_BASE = "https://newsapi.org/v2/everything"
MAX_ARTICLES  = 5  # Broj članaka po kategoriji


# ---------------------------------------------------------------------------
# RSS feed definicije (lokalni / regionalni BiH/Sarajevo)
# ---------------------------------------------------------------------------
RSS_FEEDS = {
    "sarajevo": [
        "https://www.klix.ba/rss/vijesti/sarajevo",
        "https://www.oslobodjenje.ba/rss",
        "https://www.radiosarajevo.ba/rss",
    ],
    "bih": [
        "https://www.klix.ba/rss/vijesti/bih",
        "https://www.oslobodjenje.ba/rss",
        "https://ba.n1info.com/feed/",
    ],
}

# ---------------------------------------------------------------------------
# NewsAPI upiti po kategoriji
# ---------------------------------------------------------------------------
NEWSAPI_QUERIES = {
    "ai": {
        "label": "Umjetna Inteligencija",
        "q": '("artificial intelligence" OR "machine learning" OR "ChatGPT" OR "LLM" OR "OpenAI" OR "Gemini" OR "Claude AI")',
        "language": "en",
        "sortBy": "publishedAt",
    },
    "geopolitics": {
        "label": "Geopolitika i sukobi",
        "q": '(war OR conflict OR crisis OR "military operation" OR "geopolitical" OR Ukraine OR Gaza OR Syria OR Sudan)',
        "language": "en",
        "sortBy": "publishedAt",
    },
    "astronomy": {
        "label": "Astronomija",
        "q": '(astronomy OR "space telescope" OR NASA OR ESA OR "black hole" OR "exoplanet" OR "solar system" OR "deep space")',
        "language": "en",
        "sortBy": "publishedAt",
    },
    "astrophotography": {
        "label": "Astrofotografija",
        "q": '(astrophotography OR "astronomical imaging" OR "telescope imaging" OR "deep sky object" OR "nebula photograph" OR "APOD")',
        "language": "en",
        "sortBy": "publishedAt",
    },
}


# ---------------------------------------------------------------------------
# NewsAPI dohvatanje
# ---------------------------------------------------------------------------
def _fetch_newsapi(query_cfg: dict) -> list[dict]:
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        logger.warning("NEWS_API_KEY nije postavljen — preskačem NewsAPI.")
        return []

    params = {
        "apiKey":   api_key,
        "q":        query_cfg["q"],
        "language": query_cfg.get("language", "en"),
        "sortBy":   query_cfg.get("sortBy", "publishedAt"),
        "pageSize": MAX_ARTICLES,
    }
    try:
        resp = requests.get(NEWS_API_BASE, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return [
            {
                "title":  a.get("title", ""),
                "source": a.get("source", {}).get("name", ""),
                "url":    a.get("url", ""),
                "desc":   a.get("description") or "",
            }
            for a in articles
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ][:MAX_ARTICLES]
    except Exception as e:
        logger.error(f"NewsAPI greška ({query_cfg.get('label')}): {e}")
        return []


# ---------------------------------------------------------------------------
# RSS dohvatanje
# ---------------------------------------------------------------------------
def _fetch_rss(feed_urls: list[str]) -> list[dict]:
    articles = []
    seen_titles: set[str] = set()

    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:MAX_ARTICLES]:
                title = entry.get("title", "").strip()
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)
                articles.append({
                    "title":  title,
                    "source": feed.feed.get("title", url),
                    "url":    entry.get("link", ""),
                    "desc":   entry.get("summary", "")[:200] if entry.get("summary") else "",
                })
        except Exception as e:
            logger.warning(f"RSS greška ({url}): {e}")

    # Deduplikacija i ograničenje
    return articles[:MAX_ARTICLES]


# ---------------------------------------------------------------------------
# Javni API
# ---------------------------------------------------------------------------
def fetch_all_news() -> dict[str, list[dict]]:
    """
    Vraća rječnik kategorija s listom članaka.
    Struktura: { "ai": [...], "sarajevo": [...], "bih": [...], ... }
    """
    results = {}

    # NewsAPI kategorije
    for key, cfg in NEWSAPI_QUERIES.items():
        results[key] = _fetch_newsapi(cfg)
        logger.info(f"  {cfg['label']}: {len(results[key])} članaka")

    # RSS lokalne vijesti
    results["sarajevo"] = _fetch_rss(RSS_FEEDS["sarajevo"])
    results["bih"]      = _fetch_rss(RSS_FEEDS["bih"])
    logger.info(f"  Sarajevo (RSS): {len(results['sarajevo'])} članaka")
    logger.info(f"  BiH (RSS):      {len(results['bih'])} članaka")

    return results
