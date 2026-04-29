from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import List, Optional, Tuple
from math import ceil

from src.database.models import MovieModel
from src.schemas.movies import MovieCreateSchema, MovieUpdateSchema


class MovieCRUD:
    """CRUD operations for movies"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_movie(self, movie_data: MovieCreateSchema) -> MovieModel:
        """Create a new movie"""
        movie = MovieModel(**movie_data.model_dump())
        self.db.add(movie)
        await self.db.commit()
        await self.db.refresh(movie)
        return movie

    async def get_movie_by_id(self, movie_id: int) -> Optional[MovieModel]:
        """Get a movie by ID"""
        query = select(MovieModel).where(MovieModel.id == movie_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_movies_paginated(
        self,
        page: int = 1,
        per_page: int = 10,
        filters: Optional[dict] = None
    ) -> Tuple[List[MovieModel], int]:
        """
        Get paginated list of movies

        Returns:
            Tuple of (movies list, total count)
        """
        # Build query with filters
        query = select(MovieModel)
        if filters:
            if filters.get('genre'):
                query = query.where(MovieModel.genre.contains(filters['genre']))
            if filters.get('min_score'):
                query = query.where(MovieModel.score >= filters['min_score'])
            if filters.get('max_score'):
                query = query.where(MovieModel.score <= filters['max_score'])
            if filters.get('country'):
                query = query.where(MovieModel.country == filters['country'])
            if filters.get('status'):
                query = query.where(MovieModel.status == filters['status'])

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        # Execute query
        result = await self.db.execute(query)
        movies = result.scalars().all()

        return movies, total

    async def update_movie(
        self,
        movie_id: int,
        movie_data: MovieUpdateSchema
    ) -> Optional[MovieModel]:
        """Update a movie"""
        # Check if movie exists
        existing_movie = await self.get_movie_by_id(movie_id)
        if not existing_movie:
            return None

        # Update only provided fields
        update_data = movie_data.model_dump(exclude_unset=True)
        if update_data:
            query = (
                update(MovieModel)
                .where(MovieModel.id == movie_id)
                .values(**update_data)
                .returning(MovieModel)
            )
            result = await self.db.execute(query)
            await self.db.commit()
            return result.scalar_one()

        return existing_movie

    async def delete_movie(self, movie_id: int) -> bool:
        """Delete a movie"""
        query = delete(MovieModel).where(MovieModel.id == movie_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

    async def get_movies_by_genre(
        self,
        genre: str,
        page: int = 1,
        per_page: int = 10
    ) -> Tuple[List[MovieModel], int]:
        """Get movies filtered by genre"""
        filters = {'genre': genre}
        return await self.get_movies_paginated(page, per_page, filters)

    async def get_top_rated_movies(
        self,
        limit: int = 10
    ) -> List[MovieModel]:
        """Get top rated movies"""
        query = (
            select(MovieModel)
            .where(MovieModel.score.isnot(None))
            .order_by(MovieModel.score.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_movies_by_country(
        self,
        country: str,
        page: int = 1,
        per_page: int = 10
    ) -> Tuple[List[MovieModel], int]:
        """Get movies filtered by country"""
        filters = {'country': country.upper()}
        return await self.get_movies_paginated(page, per_page, filters)
