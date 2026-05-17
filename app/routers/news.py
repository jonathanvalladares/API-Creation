from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..collectors.aggregator import run_collection
from ..collectors.sources import RSS_SOURCES, SCRAPE_SOURCES, STATIC_ARTICLES
from ..database import get_db
from ..models import NewsArticle
from ..schemas import Article, ArticleDetail, CollectResponse, NewsResponse, SourceInfo

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=NewsResponse)
def list_news(
    q: Optional[str] = Query(None, description="Search in title and summary"),
    source: Optional[str] = Query(None, description="Filter by source name (partial match)"),
    category: Optional[str] = Query(None, description="Filter by source_category: federal, media, state"),
    from_date: Optional[datetime] = Query(None, description="Filter articles published on or after this date (ISO 8601)"),
    to_date: Optional[datetime] = Query(None, description="Filter articles published on or before this date (ISO 8601)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
):
    """Return paginated SSBCI news articles with optional filters."""
    query = db.query(NewsArticle)

    if q:
        term = f"%{q}%"
        query = query.filter(
            or_(
                NewsArticle.title.ilike(term),
                NewsArticle.summary.ilike(term),
                NewsArticle.content.ilike(term),
            )
        )
    if source:
        query = query.filter(NewsArticle.source.ilike(f"%{source}%"))
    if category:
        query = query.filter(NewsArticle.source_category == category)
    if from_date:
        query = query.filter(NewsArticle.published_at >= from_date)
    if to_date:
        query = query.filter(NewsArticle.published_at <= to_date)

    total = query.count()
    articles = (
        query.order_by(NewsArticle.published_at.desc().nullslast(), NewsArticle.collected_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return NewsResponse(total=total, page=page, page_size=page_size, articles=articles)


@router.get("/latest", response_model=list[Article])
def latest_news(
    limit: int = Query(10, ge=1, le=50, description="Number of most recent articles"),
    db: Session = Depends(get_db),
):
    """Return the N most recently collected articles."""
    return (
        db.query(NewsArticle)
        .order_by(NewsArticle.collected_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/sources", response_model=list[SourceInfo])
def list_sources():
    """List all configured news sources."""
    sources = []
    for s in RSS_SOURCES:
        sources.append(SourceInfo(name=s["name"], category=s["category"], description=s["description"], url=s["url"]))
    for s in SCRAPE_SOURCES:
        sources.append(SourceInfo(name=s["name"], category=s["category"], description=s["description"], url=s["url"]))
    for s in STATIC_ARTICLES:
        sources.append(SourceInfo(name=s["title"], category=s["source_category"], description=s.get("summary", ""), url=s["url"]))
    return sources


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    """Return summary statistics about the collected news."""
    total = db.query(func.count(NewsArticle.id)).scalar()
    by_category = (
        db.query(NewsArticle.source_category, func.count(NewsArticle.id))
        .group_by(NewsArticle.source_category)
        .all()
    )
    by_source = (
        db.query(NewsArticle.source, func.count(NewsArticle.id))
        .group_by(NewsArticle.source)
        .order_by(func.count(NewsArticle.id).desc())
        .all()
    )
    latest = db.query(func.max(NewsArticle.collected_at)).scalar()
    return {
        "total_articles": total,
        "by_category": {cat: cnt for cat, cnt in by_category},
        "by_source": {src: cnt for src, cnt in by_source},
        "last_collected_at": latest,
    }


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Retrieve a single article by ID."""
    article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/collect", response_model=CollectResponse)
def collect(db: Session = Depends(get_db)):
    """
    Trigger an immediate news collection run from all sources.
    Returns the number of new articles saved.
    """
    saved, sources_queried, errors = run_collection(db)
    return CollectResponse(
        message="Collection complete",
        new_articles=saved,
        sources_queried=sources_queried,
        errors=errors,
    )
