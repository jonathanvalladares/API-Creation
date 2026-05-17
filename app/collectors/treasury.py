"""
Scrapes the official Treasury SSBCI program page for announcements
and press-release links that don't appear in RSS feeds.
"""
import logging
import re
from datetime import datetime
from typing import List, Tuple
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from ..schemas import ArticleCreate
from .sources import SCRAPE_SOURCES, SSBCI_KEYWORDS

logger = logging.getLogger(__name__)

TREASURY_BASE = "https://home.treasury.gov"
HEADERS = {
    "User-Agent": "SSBCINewsBot/1.0 (+https://github.com/jonathanvalladares/api-creation)"
}

# Patterns that suggest a link is a news/announcement item
_NEWS_PATH_RE = re.compile(
    r"/(news|press-releases?|news-releases?|announcements?|statements?|reports?)/",
    re.IGNORECASE,
)


def _is_ssbci_relevant(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in SSBCI_KEYWORDS)


def _extract_tags(text: str) -> str:
    lower = text.lower()
    return ",".join(kw for kw in SSBCI_KEYWORDS if kw in lower)


def _scrape_treasury_page(url: str, source_name: str, source_category: str) -> Tuple[List[ArticleCreate], List[str]]:
    articles: List[ArticleCreate] = []
    errors: List[str] = []

    try:
        resp = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
        resp.raise_for_status()
    except Exception as exc:
        msg = f"[Treasury] fetch {url}: {exc}"
        logger.warning(msg)
        errors.append(msg)
        return articles, errors

    soup = BeautifulSoup(resp.text, "lxml")

    seen_urls: set = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        link_text = a_tag.get_text(separator=" ", strip=True)

        if not link_text or len(link_text) < 10:
            continue

        # Resolve relative URLs
        full_url = urljoin(TREASURY_BASE, href) if href.startswith("/") else href

        # Only follow treasury.gov links
        if "treasury.gov" not in full_url:
            continue

        if full_url in seen_urls:
            continue

        if not _is_ssbci_relevant(link_text):
            continue

        seen_urls.add(full_url)
        articles.append(
            ArticleCreate(
                title=link_text[:500],
                url=full_url,
                source=source_name,
                source_category=source_category,
                summary=None,
                published_at=None,
                tags=_extract_tags(link_text),
            )
        )

    # Also look for structured content blocks (Treasury uses specific div/section patterns)
    for item in soup.select(".view-content .views-row, article, .field--name-field-news-date"):
        title_el = item.find(["h2", "h3", "h4"])
        link_el = item.find("a", href=True)
        date_el = item.find(class_=re.compile(r"date|time", re.I)) or item.find("time")

        if not title_el or not link_el:
            continue

        title = title_el.get_text(strip=True)
        href = link_el["href"]
        full_url = urljoin(TREASURY_BASE, href) if href.startswith("/") else href

        if full_url in seen_urls:
            continue
        if not _is_ssbci_relevant(title):
            continue

        published_at = None
        if date_el:
            raw = date_el.get("datetime") or date_el.get_text(strip=True)
            try:
                from dateutil import parser as dp
                published_at = dp.parse(raw)
                if published_at.tzinfo:
                    from datetime import timezone
                    published_at = published_at.astimezone(timezone.utc).replace(tzinfo=None)
            except Exception:
                pass

        seen_urls.add(full_url)
        articles.append(
            ArticleCreate(
                title=title[:500],
                url=full_url,
                source=source_name,
                source_category=source_category,
                summary=None,
                published_at=published_at,
                tags=_extract_tags(title),
            )
        )

    logger.info("[Treasury] %s: found %d relevant links", source_name, len(articles))
    return articles, errors


def collect_treasury() -> Tuple[List[ArticleCreate], List[str]]:
    all_articles: List[ArticleCreate] = []
    all_errors: List[str] = []

    for source in SCRAPE_SOURCES:
        arts, errs = _scrape_treasury_page(
            source["url"], source["name"], source["category"]
        )
        all_articles.extend(arts)
        all_errors.extend(errs)

    return all_articles, all_errors
