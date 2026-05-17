from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from .database import Base


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(2000), nullable=False)
    source = Column(String(100), nullable=False)
    source_category = Column(String(100))          # e.g. "federal", "state", "media"
    summary = Column(Text)
    content = Column(Text)
    published_at = Column(DateTime, index=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tags = Column(String(500))                     # comma-separated keywords found in article

    __table_args__ = (UniqueConstraint("url", name="uq_article_url"),)
