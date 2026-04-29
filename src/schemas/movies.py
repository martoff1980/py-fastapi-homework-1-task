from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date as date_db


class MovieDetailResponseSchema(BaseModel):
    """Схема для детальной информации о фильме"""
    id: int
    name: str
    date: Optional[date_db] = None
    score: Optional[float] = None
    genre: Optional[str] = None
    overview: Optional[str] = None
    crew: Optional[str] = None
    orig_title: Optional[str] = None
    status: Optional[str] = None
    orig_lang: Optional[str] = None
    budget: Optional[float] = None
    revenue: Optional[float] = None
    country: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MovieListResponseSchema(BaseModel):
    """Схема для пагинированного списка фильмов"""
    movies: List[MovieDetailResponseSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int

    model_config = ConfigDict(from_attributes=True)
