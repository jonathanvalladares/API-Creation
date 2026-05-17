"""
Tests for the SSBCI News API.
Uses an in-memory SQLite DB so no files are left on disk.
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.database import Base, get_db
from app.main import app
from app.models import NewsArticle

# StaticPool ensures all sessions share one connection so in-memory SQLite is visible everywhere
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db():
    session = TestSessionLocal()
    yield session
    session.close()


def _seed_articles(db, n=5):
    articles = []
    for i in range(n):
        a = NewsArticle(
            title=f"SSBCI Article {i}",
            url=f"https://example.com/news/{i}",
            source="Test Source",
            source_category="federal",
            summary=f"Summary for article {i} about SSBCI",
            published_at=datetime(2024, 1, i + 1),
            collected_at=datetime(2024, 1, i + 1),
            tags="ssbci",
        )
        db.add(a)
        articles.append(a)
    db.commit()
    return articles


# ── Health endpoints ──────────────────────────────────────────────────────────

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "SSBCI News API"
    assert "endpoints" in data


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── List news ─────────────────────────────────────────────────────────────────

def test_list_news_empty(client):
    r = client.get("/news")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["articles"] == []


def test_list_news_returns_articles(client, db):
    _seed_articles(db, 3)
    r = client.get("/news")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert len(data["articles"]) == 3


def test_list_news_pagination(client, db):
    _seed_articles(db, 5)
    r = client.get("/news?page=1&page_size=2")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 5
    assert len(data["articles"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_list_news_second_page(client, db):
    _seed_articles(db, 5)
    r = client.get("/news?page=2&page_size=2")
    assert r.status_code == 200
    data = r.json()
    assert len(data["articles"]) == 2


def test_list_news_search(client, db):
    _seed_articles(db, 3)
    r = client.get("/news?q=Article+1")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert "Article 1" in data["articles"][0]["title"]


def test_list_news_filter_category(client, db):
    _seed_articles(db, 3)
    db_session = TestSessionLocal()
    db_session.add(NewsArticle(
        title="Media SSBCI story",
        url="https://example.com/media/1",
        source="CNN",
        source_category="media",
        collected_at=datetime.utcnow(),
    ))
    db_session.commit()
    db_session.close()

    r = client.get("/news?category=media")
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_list_news_filter_source(client, db):
    _seed_articles(db, 3)
    r = client.get("/news?source=Test+Source")
    assert r.status_code == 200
    assert r.json()["total"] == 3


def test_list_news_date_filter(client, db):
    _seed_articles(db, 5)
    r = client.get("/news?from_date=2024-01-03T00:00:00")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3  # articles 3,4,5


# ── Latest ────────────────────────────────────────────────────────────────────

def test_latest_news(client, db):
    _seed_articles(db, 5)
    r = client.get("/news/latest?limit=3")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3


def test_latest_news_default_limit(client, db):
    _seed_articles(db, 5)
    r = client.get("/news/latest")
    assert r.status_code == 200
    assert len(r.json()) == 5  # fewer than default 10


# ── Article detail ────────────────────────────────────────────────────────────

def test_get_article(client, db):
    arts = _seed_articles(db, 1)
    article_id = arts[0].id
    r = client.get(f"/news/{article_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == article_id
    assert "SSBCI" in data["title"]


def test_get_article_not_found(client):
    r = client.get("/news/99999")
    assert r.status_code == 404


# ── Sources ───────────────────────────────────────────────────────────────────

def test_list_sources(client):
    r = client.get("/news/sources")
    assert r.status_code == 200
    sources = r.json()
    assert len(sources) > 0
    categories = {s["category"] for s in sources}
    assert "federal" in categories
    names = [s["name"] for s in sources]
    assert any("Treasury" in n or "Federal" in n or "Google" in n for n in names)


# ── Stats ─────────────────────────────────────────────────────────────────────

def test_stats_empty(client):
    r = client.get("/news/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total_articles"] == 0


def test_stats_with_data(client, db):
    _seed_articles(db, 4)
    r = client.get("/news/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total_articles"] == 4
    assert "federal" in data["by_category"]
    assert "Test Source" in data["by_source"]


# ── Collect endpoint ──────────────────────────────────────────────────────────

def test_collect_endpoint(client):
    with patch("app.routers.news.run_collection") as mock_collect:
        mock_collect.return_value = (5, 7, [])
        r = client.post("/news/collect")
    assert r.status_code == 200
    data = r.json()
    assert data["new_articles"] == 5
    assert data["sources_queried"] == 7
    assert data["errors"] == []


def test_collect_endpoint_with_errors(client):
    with patch("app.routers.news.run_collection") as mock_collect:
        mock_collect.return_value = (2, 7, ["RSS feed timeout"])
        r = client.post("/news/collect")
    assert r.status_code == 200
    data = r.json()
    assert data["new_articles"] == 2
    assert len(data["errors"]) == 1


# ── Deduplication ─────────────────────────────────────────────────────────────

def test_duplicate_url_not_saved(db):
    from app.collectors.aggregator import _save_articles
    from app.schemas import ArticleCreate

    art = ArticleCreate(
        title="SSBCI Test",
        url="https://example.com/unique",
        source="Test",
        source_category="federal",
    )
    saved1 = _save_articles(db, [art])
    saved2 = _save_articles(db, [art])  # duplicate
    assert saved1 == 1
    assert saved2 == 0
