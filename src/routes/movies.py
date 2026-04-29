from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db, MovieModel

from typing import Optional
from math import ceil

from src.schemas.movies import MovieDetailResponseSchema, MovieListResponseSchema

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=MovieListResponseSchema)
async def get_movies(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=20, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of movies.

    - **page**: Page number (>= 1)
    - **per_page**: Number of movies per page (1-20)
    """

    # Get total count of movies
    total_count_query = select(func.count()).select_from(MovieModel)
    total_count_result = await db.execute(total_count_query)
    total_items = total_count_result.scalar()

    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    # Calculate total pages
    total_pages = ceil(total_items / per_page)

    # Check if requested page exceeds total pages
    if page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found."
        )

    # Calculate offset
    offset = (page - 1) * per_page

    # Get movies for current page
    query = select(MovieModel).offset(offset).limit(per_page)
    result = await db.execute(query)
    movies = result.scalars().all()

    # If no movies on current page (should not happen if page <= total_pages, but just in case)
    if not movies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found."
        )

    # Convert to response schema
    movies_response = [MovieDetailResponseSchema.model_validate(movie) for movie in movies]

    # Generate prev_page and next_page URLs
    base_url = "/movies/"

    prev_page_url = f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
    next_page_url = f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None

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
    query = select(MovieModel).where(MovieModel.id == movie_id)
    result = await db.execute(query)
    movie = result.scalar_one_or_none()

    if movie is None:
        raise HTTPException(
            status_code=404,
            detail="Movie with the given ID was not found."
        )

    return MovieDetailResponseSchema.model_validate(movie)
