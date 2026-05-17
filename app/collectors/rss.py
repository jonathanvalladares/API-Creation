"""
RSS collector using stdlib xml.etree.ElementTree so no sgmllib dependency is needed.
Supports Atom and RSS 2.0 feeds.
"""
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import httpx
from dateutil import parser as dateparser

from ..schemas import ArticleCreate
from .sources import RSS_SOURCES, SSBCI_KEYWORDS

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "SSBCINewsBot/1.0 (+https://github.com/jonathanvalladares/api-creation)"
}

# XML namespaces commonly found in RSS/Atom feeds
_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "media": "http://search.yahoo.com/mrss/",
}


def _text(el: Optional[ET.Element]) -> str:
    if el is None:
        return ""
    return (el.text or "").strip()


def _parse_date(raw: str) -> Optional[datetime]:
    if not raw:
        return None
    try:
        dt = dateparser.parse(raw)
        if dt and dt.tzinfo:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        return None


def _is_ssbci_relevant(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    return any(kw in text for kw in SSBCI_KEYWORDS)


def _extract_tags(title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    return ",".join(kw for kw in SSBCI_KEYWORDS if kw in text)


def _parse_rss_feed(xml_text: str) -> List[dict]:
    """Parse RSS 2.0 or Atom feed XML; return list of entry dicts."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError(f"XML parse error: {exc}") from exc

    entries = []
    tag = root.tag.lower()

    if "atom" in tag or root.tag == "{http://www.w3.org/2005/Atom}feed":
        # Atom feed
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = _text(entry.find("{http://www.w3.org/2005/Atom}title"))
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            url = ""
            if link_el is not None:
                url = link_el.get("href", "") or _text(link_el)
            summary = _text(entry.find("{http://www.w3.org/2005/Atom}summary")) or \
                      _text(entry.find("{http://www.w3.org/2005/Atom}content"))
            date_raw = _text(entry.find("{http://www.w3.org/2005/Atom}published")) or \
                       _text(entry.find("{http://www.w3.org/2005/Atom}updated"))
            entries.append({"title": title, "url": url, "summary": summary, "date": date_raw})
    else:
        # RSS 2.0 — channel/item
        for item in root.iter("item"):
            title = _text(item.find("title"))
            url = _text(item.find("link"))
            if not url:
                guid = item.find("guid")
                if guid is not None and guid.get("isPermaLink", "true").lower() != "false":
                    url = _text(guid)
            summary = _text(item.find("description"))
            date_raw = _text(item.find("pubDate")) or _text(item.find("{http://purl.org/dc/elements/1.1/}date"))
            entries.append({"title": title, "url": url, "summary": summary, "date": date_raw})

    return entries


def collect_rss() -> Tuple[List[ArticleCreate], List[str]]:
    articles: List[ArticleCreate] = []
    errors: List[str] = []

    for source in RSS_SOURCES:
        try:
            resp = httpx.get(source["url"], headers=HEADERS, timeout=15, follow_redirects=True)
            resp.raise_for_status()
            entries = _parse_rss_feed(resp.text)
        except Exception as exc:
            msg = f"[RSS] {source['name']}: {exc}"
            logger.warning(msg)
            errors.append(msg)
            continue

        added = 0
        for entry in entries:
            title = entry["title"].strip()
            url = entry["url"].strip()
            summary = entry["summary"]

            if not title or not url:
                continue

            # For non-Google-News feeds, filter to SSBCI-relevant entries only
            if "google.com" not in source["url"] and not _is_ssbci_relevant(title, summary):
                continue

            published_at = _parse_date(entry["date"])
            articles.append(
                ArticleCreate(
                    title=title,
                    url=url,
                    source=source["name"],
                    source_category=source["category"],
                    summary=summary[:2000] if summary else None,
                    published_at=published_at,
                    tags=_extract_tags(title, summary),
                )
            )
            added += 1

        logger.info("[RSS] %s: fetched %d entries, %d SSBCI-relevant", source["name"], len(entries), added)

    return articles, errors
