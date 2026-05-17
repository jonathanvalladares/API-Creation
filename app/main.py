import logging
import sys
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from .database import SessionLocal, engine
from .models import Base
from .routers import news as news_router

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler(timezone="UTC")


def _scheduled_collect():
    from .collectors.aggregator import run_collection
    db = SessionLocal()
    try:
        saved, sources, errors = run_collection(db)
        logger.info("[Scheduler] Collected %d new articles from %d sources", saved, sources)
        if errors:
            logger.warning("[Scheduler] %d errors: %s", len(errors), errors[:3])
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run once on startup, then every 6 hours
    scheduler.add_job(_scheduled_collect, "interval", hours=6, id="collect_news")
    scheduler.start()
    logger.info("Scheduler started (6-hour interval). Running initial collection…")
    _scheduled_collect()
    yield
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped.")


app = FastAPI(
    title="SSBCI News API",
    description=(
        "Aggregates news, announcements, and regulatory filings related to the "
        "U.S. Treasury State Small Business Credit Initiative (SSBCI). "
        "Sources include Google News, the Federal Register, Treasury press releases, "
        "the SBA, and the official Treasury SSBCI program page."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(news_router.router)


@app.get("/", tags=["health"])
def root():
    return {
        "service": "SSBCI News API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "list_news": "GET /news",
            "latest_news": "GET /news/latest",
            "article_detail": "GET /news/{id}",
            "sources": "GET /news/sources",
            "stats": "GET /news/stats",
            "trigger_collection": "POST /news/collect",
        },
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
