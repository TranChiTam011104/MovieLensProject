"""
Movies Router - Endpoints for movie information.

ENDPOINTS:
- GET /v1/movies/{movie_id} - Get movie details
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional

# Import models
from ..models import (
    MovieDetails,
    ErrorResponse
)

router = APIRouter(prefix="/v1", tags=["Movies"])

# In-memory movie cache (in production, use a database)
_movies_cache: Optional[dict] = None


def get_movies_cache() -> dict:
    """
    Get movies cache. Loads from data if not already cached.
    
    Returns:
        Dict mapping movie_id -> movie data
    """
    global _movies_cache
    
    if _movies_cache is not None:
        return _movies_cache
    
    # Try to load from data
    try:
        from ...data.load import load_movies
        from ...data.preprocess import process_movies
        
        movies_df = load_movies()
        processed = process_movies(movies_df)
        
        _movies_cache = {
            row['movie_id']: row.to_dict()
            for _, row in processed.iterrows()
        }
    except Exception as e:
        print(f"Warning: Could not load movies cache: {e}")
        _movies_cache = {}
    
    return _movies_cache


@router.get(
    "/movies/{movie_id}",
    response_model=MovieDetails,
    responses={
        404: {"model": ErrorResponse}
    }
)
async def get_movie_details(
    movie_id: int = Path(..., ge=1, description="Movie ID")
):
    """
    Get detailed information about a specific movie.
    
    Returns metadata including:
    - Title and release year
    - Genres
    - Average rating
    - Number of ratings
    
    **Use cases**:
    - Movie detail page
    - Populate UI with movie info
    - Metadata lookup for recommendations
    """
    movies = get_movies_cache()
    
    if movie_id not in movies:
        raise HTTPException(
            status_code=404,
            detail=f"Movie with ID {movie_id} not found"
        )
    
    movie = movies[movie_id]
    
    return MovieDetails(
        movie_id=movie_id,
        title=movie.get('title', 'Unknown'),
        genres=movie.get('genres', []),
        release_year=movie.get('release_year'),
        avg_rating=round(movie.get('avg_rating'), 2) if movie.get('avg_rating') else None,
        n_ratings=movie.get('n_ratings', 0)
    )


@router.get(
    "/movies",
    response_model=List[MovieDetails],
    responses={
        404: {"model": ErrorResponse}
    }
)
async def list_movies(
    limit: int = Query(20, ge=1, le=100, description="Number of movies to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List movies with pagination.
    
    Returns a list of movies sorted by movie_id.
    
    **Use cases**:
    - Browse movies
    - Search/filter interface
    - Admin dashboard
    """
    movies = get_movies_cache()
    
    all_movie_ids = sorted(movies.keys())
    page_ids = all_movie_ids[offset:offset + limit]
    
    return [
        MovieDetails(
            movie_id=mid,
            title=movies[mid].get('title', 'Unknown'),
            genres=movies[mid].get('genres', []),
            release_year=movies[mid].get('release_year'),
            avg_rating=round(movies[mid].get('avg_rating'), 2) if movies[mid].get('avg_rating') else None,
            n_ratings=movies[mid].get('n_ratings', 0)
        )
        for mid in page_ids
    ]
