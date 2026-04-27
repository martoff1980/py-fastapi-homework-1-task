from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from math import ceil

from database import get_db
from crud.movies import MovieCRUD
from schemas.movies import (
    MovieDetailResponseSchema,
    MovieListResponseSchema,
    MovieCreateSchema,
    MovieUpdateSchema
)

router = APIRouter(prefix="/theater/movies", tags=["movies"])


@router.get("/", response_model=MovieListResponseSchema)
async def get_movies(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=20, description="Items per page"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum score"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum score"),
    country: Optional[str] = Query(None, min_length=2, max_length=2, description="Country code (2 letters)"),
    status: Optional[str] = Query(None, description="Release status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of movies with optional filters.

    - **page**: Page number (>= 1)
    - **per_page**: Number of movies per page (1-20)
    - **genre**: Filter by genre
    - **min_score**: Minimum score filter
    - **max_score**: Maximum score filter
    - **country**: Filter by country code (2 letters)
    - **status**: Filter by release status
    """
    crud = MovieCRUD(db)

    # Prepare filters
    filters = {}
    if genre:
        filters['genre'] = genre
    if min_score is not None:
        filters['min_score'] = min_score
    if max_score is not None:
        filters['max_score'] = max_score
    if country:
        filters['country'] = country.upper()
    if status:
        filters['status'] = status

    # Get movies with pagination
    movies, total_items = await crud.get_movies_paginated(page, per_page, filters)

    if total_items == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found."
        )

    # Calculate total pages
    total_pages = ceil(total_items / per_page)

    # Convert to response schema
    movies_response = [MovieDetailResponseSchema.model_validate(movie) for movie in movies]

    # Generate prev_page and next_page URLs
    base_url = "/theater/movies/"
    params = []
    if genre:
        params.append(f"genre={genre}")
    if min_score is not None:
        params.append(f"min_score={min_score}")
    if max_score is not None:
        params.append(f"max_score={max_score}")
    if country:
        params.append(f"country={country}")
    if status:
        params.append(f"status={status}")

    param_str = "&".join(params)
    base_url_with_filters = base_url + (f"?{param_str}&" if param_str else "?")

    prev_page_url = None
    next_page_url = None

    if page > 1:
        prev_page_url = f"{base_url_with_filters}page={page - 1}&per_page={per_page}"
    else:
        # Remove the extra '&' or '?' if no filters
        if param_str:
            prev_page_url = f"{base_url}?{param_str}&page={page - 1}&per_page={per_page}"
        else:
            prev_page_url = f"{base_url}?page={page - 1}&per_page={per_page}"

    if page < total_pages:
        if param_str:
            next_page_url = f"{base_url}?{param_str}&page={page + 1}&per_page={per_page}"
        else:
            next_page_url = f"{base_url}?page={page + 1}&per_page={per_page}"

    return MovieListResponseSchema(
        movies=movies_response,
        prev_page=prev_page_url,
        next_page=next_page_url,
        total_pages=total_pages,
        total_items=total_items
    )


@router.get("/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_by_id(
    movie_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a movie by its ID.

    - **movie_id**: The ID of the movie to fetch
    """
    crud = MovieCRUD(db)
    movie = await crud.get_movie_by_id(movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found."
        )

    return MovieDetailResponseSchema.model_validate(movie)


@router.post("/", response_model=MovieDetailResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_data: MovieCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new movie.

    - **movie_data**: Movie information
    """
    crud = MovieCRUD(db)
    movie = await crud.create_movie(movie_data)
    return MovieDetailResponseSchema.model_validate(movie)


@router.put("/{movie_id}/", response_model=MovieDetailResponseSchema)
async def update_movie(
    movie_id: int,
    movie_data: MovieUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing movie.

    - **movie_id**: ID of the movie to update
    - **movie_data**: Updated movie information
    """
    crud = MovieCRUD(db)
    movie = await crud.update_movie(movie_id, movie_data)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found."
        )

    return MovieDetailResponseSchema.model_validate(movie)


@router.delete("/{movie_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a movie.

    - **movie_id**: ID of the movie to delete
    """
    crud = MovieCRUD(db)
    deleted = await crud.delete_movie(movie_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found."
        )

    return None


@router.get("/top-rated/", response_model=List[MovieDetailResponseSchema])
async def get_top_rated_movies(
    limit: int = Query(10, ge=1, le=50, description="Number of top rated movies"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top rated movies.

    - **limit**: Number of movies to return (1-50)
    """
    crud = MovieCRUD(db)
    movies = await crud.get_top_rated_movies(limit)

    if not movies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found."
        )

    return [MovieDetailResponseSchema.model_validate(movie) for movie in movies]


@router.get("/by-genre/{genre}/", response_model=MovieListResponseSchema)
async def get_movies_by_genre(
    genre: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Get movies filtered by genre.

    - **genre**: Genre name
    - **page**: Page number
    - **per_page**: Items per page
    """
    crud = MovieCRUD(db)
    movies, total_items = await crud.get_movies_by_genre(genre, page, per_page)

    if total_items == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No movies found in genre '{genre}'."
        )

    total_pages = ceil(total_items / per_page)
    movies_response = [MovieDetailResponseSchema.model_validate(movie) for movie in movies]

    base_url = f"/theater/movies/by-genre/{genre}/"

    return MovieListResponseSchema(
        movies=movies_response,
        prev_page=f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None,
        next_page=f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None,
        total_pages=total_pages,
        total_items=total_items
    )
