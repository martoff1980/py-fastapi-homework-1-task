from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date


class MovieDetailResponseSchema(BaseModel):
    """Schema for detailed movie information"""
    id: int
    name: str
    release_date: Optional[date] = None
    score: Optional[float] = None
    genre: Optional[str] = None
    overview: Optional[str] = None
    crew: Optional[str] = None
    orig_title: Optional[str] = None
    status: Optional[str] = None
    orig_lang: Optional[str] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True


class MovieListResponseSchema(BaseModel):
    """Schema for paginated movie list"""
    movies: List[MovieDetailResponseSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int

    class Config:
        from_attributes = True


class MovieCreateSchema(BaseModel):
    """Schema for creating a new movie"""
    name: str = Field(..., min_length=1, max_length=255)
    release_date: Optional[date] = None
    score: Optional[float] = Field(None, ge=0, le=100)
    genre: Optional[str] = None
    overview: Optional[str] = None
    crew: Optional[str] = None
    orig_title: Optional[str] = None
    status: Optional[str] = None
    orig_lang: Optional[str] = None
    budget: Optional[int] = Field(None, ge=0)
    revenue: Optional[int] = Field(None, ge=0)
    country: Optional[str] = Field(None, max_length=2)

    class Config:
        from_attributes = True


class MovieUpdateSchema(BaseModel):
    """Schema for updating a movie"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    release_date: Optional[date] = None
    score: Optional[float] = Field(None, ge=0, le=100)
    genre: Optional[str] = None
    overview: Optional[str] = None
    crew: Optional[str] = None
    orig_title: Optional[str] = None
    status: Optional[str] = None
    orig_lang: Optional[str] = None
    budget: Optional[int] = Field(None, ge=0)
    revenue: Optional[int] = Field(None, ge=0)
    country: Optional[str] = Field(None, max_length=2)

    class Config:
        from_attributes = True
