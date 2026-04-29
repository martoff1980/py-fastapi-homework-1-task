from pydantic import BaseModel, Field, ConfigDict
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


class MovieCreateSchema(BaseModel):
    """Schema for creating a new movie"""
    name: str = Field(..., min_length=1, max_length=255)
    date: Optional[date_db] = None
    score: Optional[float] = Field(None, ge=0, le=100)
    genre: Optional[str] = None
    overview: Optional[str] = None
    crew: Optional[str] = None
    orig_title: Optional[str] = None
    status: Optional[str] = None
    orig_lang: Optional[str] = None
    budget: Optional[float] = Field(None, ge=0)
    revenue: Optional[float] = Field(None, ge=0)
    country: Optional[str] = Field(None, max_length=2)

    model_config = ConfigDict(from_attributes=True)


class MovieUpdateSchema(BaseModel):
    """Schema for updating a movie"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    date: Optional[date_db] = None
    score: Optional[float] = Field(None, ge=0, le=100)
    genre: Optional[str] = None
    overview: Optional[str] = None
    crew: Optional[str] = None
    orig_title: Optional[str] = None
    status: Optional[str] = None
    orig_lang: Optional[str] = None
    budget: Optional[float] = Field(None, ge=0)
    revenue: Optional[float] = Field(None, ge=0)
    country: Optional[str] = Field(None, max_length=2)

    model_config = ConfigDict(from_attributes=True)

