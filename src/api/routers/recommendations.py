"""
Recommendations Router - Endpoints for movie recommendations.

ENDPOINTS:
- GET /v1/recommend/users/{user_id} - Get personalized recommendations for a user
- GET /v1/movies/{movie_id}/similar - Get similar movies
- GET /v1/users/{user_id}/similar - Get similar users
"""

from fastapi import APIRouter, HTTPException, Path, Query
from typing import Optional

# Import models
from ..models import (
    RecommendationResponse,
    MovieRecommendation,
    SimilarMoviesResponse,
    SimilarMovie,
    SimilarUsersResponse,
    SimilarUser,
    ErrorResponse,
    ValidationError
)

# Import services
from ..services.recommendation_engine import get_engine
from ..services.similarity_service import get_similarity_service

router = APIRouter(prefix="/v1", tags=["Recommendations"])


# ============================================================
# RECOMMENDATIONS ENDPOINT
# ============================================================

@router.get(
    "/recommend/users/{user_id}",
    response_model=RecommendationResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ValidationError},
        429: {"model": ErrorResponse}
    }
)
async def get_recommendations(
    user_id: int = Path(..., ge=1, le=943, description="User ID (1-943)"),
    n: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    exclude_watched: bool = Query(True, description="Exclude movies user has rated"),
    min_rating: float = Query(0, ge=0, le=5, description="Minimum predicted rating")
):
    """
    Get personalized movie recommendations for a user.
    
    Returns a list of movies the user is likely to enjoy, sorted by predicted rating.
    
    **Algorithm**: SVD-based Collaborative Filtering
    
    **Use cases**:
    - Homepage "Movies for you"
    - Push notifications
    - Landing page for logged-in users
    """
    # Get engine
    engine = get_engine()
    
    # Check if model is loaded
    if not engine.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please wait for initialization."
        )
    
    # Validate user exists (basic check)
    # In production, you'd query the database
    if user_id < 1 or user_id > 943:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} does not exist"
        )
    
    try:
        # Get recommendations from engine
        recommendations = engine.get_recommendations(
            user_id=user_id,
            n=n,
            exclude_watched=exclude_watched,
            min_rating=min_rating
        )
        
        # Convert to response model
        movie_recs = [
            MovieRecommendation(
                movie_id=rec['movie_id'],
                title=rec.get('title', 'Unknown'),
                genres=rec.get('genres', []),
                predicted_rating=round(rec['predicted_rating'], 2),
                confidence=round(rec.get('confidence', 0.8), 2)
            )
            for rec in recommendations
        ]
        
        return RecommendationResponse(
            user_id=user_id,
            n_recommendations=len(movie_recs),
            recommendations=movie_recs,
            message=None if movie_recs else "No recommendations available for this user"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


# ============================================================
# SIMILAR MOVIES ENDPOINT
# ============================================================

@router.get(
    "/movies/{movie_id}/similar",
    response_model=SimilarMoviesResponse,
    responses={
        404: {"model": ErrorResponse}
    }
)
async def get_similar_movies(
    movie_id: int = Path(..., ge=1, description="Reference movie ID"),
    n: int = Query(10, ge=1, le=50, description="Number of similar movies"),
    min_similarity: float = Query(0, ge=0, le=1, description="Minimum similarity threshold")
):
    """
    Get movies similar to the specified movie.
    
    Uses **Item-based Collaborative Filtering** on SVD latent factors.
    
    **Algorithm**:
    1. Extract movie's latent factor vector from SVD
    2. Compute cosine similarity with all other movies
    3. Return top-N most similar movies
    
    **Use cases**:
    - "Movies similar to this"
    - "You might also like"
    - Cross-selling recommendations
    """
    # Get similarity service
    similarity_service = get_similarity_service()
    
    if not similarity_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Similarity service not loaded. Please wait for initialization."
        )
    
    try:
        # Get similar movies
        similar = similarity_service.get_similar_movies(
            movie_id=movie_id,
            n=n,
            min_similarity=min_similarity
        )
        
        if not similar:
            return SimilarMoviesResponse(
                movie_id=movie_id,
                title=f"Movie {movie_id}",
                n_similar=0,
                similar_movies=[],
                message="Movie not found or no similar movies meet the threshold."
            )
        
        # Get reference movie title
        ref_title = similar[0].get('title', f'Movie {movie_id}') if similar else f'Movie {movie_id}'
        
        # Convert to response model
        similar_movies = [
            SimilarMovie(
                movie_id=item['movie_id'],
                title=item.get('title', 'Unknown'),
                genres=item.get('genres', []),
                similarity_score=round(item['similarity_score'], 4),
                avg_rating=round(item.get('avg_rating'), 2) if item.get('avg_rating') else None
            )
            for item in similar
        ]
        
        # Get reference movie title from first result's context or query
        # For now, use a placeholder - in real app, query movie DB
        ref_title = f"Movie {movie_id}"  # TODO: Fetch from DB
        
        return SimilarMoviesResponse(
            movie_id=movie_id,
            title=ref_title,
            n_similar=len(similar_movies),
            similar_movies=similar_movies,
            message=None if similar_movies else "No movies meet the minimum similarity threshold"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding similar movies: {str(e)}"
        )


# ============================================================
# SIMILAR USERS ENDPOINT
# ============================================================

@router.get(
    "/users/{user_id}/similar",
    response_model=SimilarUsersResponse,
    responses={
        404: {"model": ErrorResponse}
    }
)
async def get_similar_users(
    user_id: int = Path(..., ge=1, le=943, description="Reference user ID"),
    n: int = Query(10, ge=1, le=50, description="Number of similar users"),
    min_similarity: float = Query(0, ge=0, le=1, description="Minimum similarity threshold")
):
    """
    Get users with similar preferences to the specified user.
    
    Uses **User-based Collaborative Filtering** on SVD latent factors.
    
    **Algorithm**:
    1. Extract user's latent factor vector from SVD
    2. Compute cosine similarity with all other users
    3. Return top-N most similar users
    
    **Use cases**:
    - User segmentation / clustering
    - Community insights
    - Social features ("Connect with similar users")
    - Cold-start recommendations (borrow from similar users)
    """
    # Get similarity service
    similarity_service = get_similarity_service()
    
    if not similarity_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Similarity service not loaded. Please wait for initialization."
        )
    
    # Validate user
    if user_id < 1 or user_id > 943:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} does not exist"
        )
    
    try:
        # Get similar users
        similar = similarity_service.get_similar_users(
            user_id=user_id,
            n=n,
            min_similarity=min_similarity
        )
        
        # Convert to response model
        similar_users = [
            SimilarUser(
                user_id=item['user_id'],
                similarity_score=round(item['similarity_score'], 4),
                common_ratings=item.get('common_ratings', 0),
                top_common_genres=item.get('top_common_genres', [])
            )
            for item in similar
        ]
        
        return SimilarUsersResponse(
            user_id=user_id,
            n_similar=len(similar_users),
            similar_users=similar_users,
            message=None if similar_users else "Limited similar users found for this user"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding similar users: {str(e)}"
        )
