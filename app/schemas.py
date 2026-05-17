from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ArticleBase(BaseModel):
    title: str
    url: str
    source: str
    source_category: Optional[str] = None
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    tags: Optional[str] = None


class ArticleCreate(ArticleBase):
    content: Optional[str] = None
    collected_at: Optional[datetime] = None


class Article(ArticleBase):
    id: int
    collected_at: datetime

    model_config = {"from_attributes": True}


class ArticleDetail(Article):
    content: Optional[str] = None


class NewsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    articles: List[Article]


class CollectResponse(BaseModel):
    message: str
    new_articles: int
    sources_queried: int
    errors: List[str]


class SourceInfo(BaseModel):
    name: str
    category: str
    description: str
    url: str
