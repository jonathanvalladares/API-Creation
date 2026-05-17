"""
Orchestrates all collectors and persists de-duplicated articles to the DB.
"""
import logging
from datetime import datetime
from typing import List, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import NewsArticle
from ..schemas import ArticleCreate
from .rss import collect_rss
from .treasury import collect_treasury

logger = logging.getLogger(__name__)


def _save_articles(db: Session, articles: List[ArticleCreate]) -> int:
    saved = 0
    for art in articles:
        row = NewsArticle(
            title=art.title,
            url=art.url,
            source=art.source,
            source_category=art.source_category,
            summary=art.summary,
            content=art.content,
            published_at=art.published_at,
            collected_at=datetime.utcnow(),
            tags=art.tags,
        )
        db.add(row)
        try:
            db.flush()
            saved += 1
        except IntegrityError:
            db.rollback()  # duplicate URL — skip
    db.commit()
    return saved


def run_collection(db: Session) -> Tuple[int, int, List[str]]:
    """
    Run all collectors and persist results.
    Returns (new_articles_saved, sources_queried, errors).
    """
    all_articles: List[ArticleCreate] = []
    all_errors: List[str] = []

    rss_articles, rss_errors = collect_rss()
    all_articles.extend(rss_articles)
    all_errors.extend(rss_errors)

    treasury_articles, treasury_errors = collect_treasury()
    all_articles.extend(treasury_articles)
    all_errors.extend(treasury_errors)

    from .sources import RSS_SOURCES, SCRAPE_SOURCES, STATIC_ARTICLES
    for s in STATIC_ARTICLES:
        all_articles.append(ArticleCreate(**s))
    sources_queried = len(RSS_SOURCES) + len(SCRAPE_SOURCES)

    saved = _save_articles(db, all_articles)
    logger.info("Collection complete: %d new articles saved (of %d collected)", saved, len(all_articles))
    return saved, sources_queried, all_errors
