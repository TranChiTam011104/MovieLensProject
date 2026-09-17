"""
Pydantic Models - Request/Response schemas cho API.

File này định nghĩa:
- Request models: dữ liệu gửi lên từ client
- Response models: dữ liệu trả về cho client
- Internal models: dùng nội bộ service
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================
# COMMON / SHARED MODELS
# ============================================================

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., description="HTTP status code")


class ValidationErrorDetail(BaseModel):
    """Detail of a single validation error."""
    field: str = Field(..., description="Field name")
    issue: str = Field(..., description="Validation issue")


class ValidationError(ErrorResponse):
    """Validation error response."""
    details: List[ValidationErrorDetail] = Field(default_factory=list)


# ============================================================
# HEALTH MODELS
# ============================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current server time")
    model_version: str = Field(..., description="Model version")


# ============================================================
# MOVIE MODELS
# ============================================================

class MovieRecommendation(BaseModel):
    """Single movie in recommendation list."""
    movie_id: int = Field(..., description="Unique movie identifier")
    title: str = Field(..., description="Movie title with year")
    genres: List[str] = Field(default_factory=list, description="Movie genres")
    predicted_rating: float = Field(
        ...,
        ge=1,
        le=5,
        description="Predicted rating (1-5 stars)"
    )
    actual_rating: Optional[float] = Field(
        None,
        description="User's actual rating if exists in test data"
    )


class RecommendationResponse(BaseModel):
    """Response for user recommendations endpoint."""
    user_id: int = Field(..., description="User ID requested")
    n_recommendations: int = Field(..., description="Number of recommendations")
    recommendations: List[MovieRecommendation] = Field(
        default_factory=list,
        description="List of recommended movies"
    )
    message: Optional[str] = Field(
        None,
        description="Optional message (e.g., when no recommendations)"
    )


class MovieDetails(BaseModel):
    """Movie details response."""
    movie_id: int = Field(..., description="Movie ID")
    title: str = Field(..., description="Movie title")
    genres: List[str] = Field(default_factory=list, description="Movie genres")
    release_year: Optional[int] = Field(None, description="Release year")
    avg_rating: Optional[float] = Field(None, description="Average rating")
    n_ratings: int = Field(..., description="Number of ratings")


# ============================================================
# PREDICTION MODELS
# ============================================================

class PredictionResponse(BaseModel):
    """Rating prediction response."""
    user_id: int = Field(..., description="User ID")
    movie_id: int = Field(..., description="Movie ID")
    predicted_rating: float = Field(
        ...,
        ge=1,
        le=5,
        description="Predicted rating (1-5 scale)"
    )
    actual_rating: Optional[float] = Field(
        None,
        description="User's actual rating if exists in test data"
    )


# ============================================================
# SIMILARITY MODELS (Item-based & User-based)
# ============================================================

class SimilarMovie(BaseModel):
    """Similar movie result."""
    movie_id: int = Field(..., description="Similar movie ID")
    title: str = Field(..., description="Movie title")
    genres: List[str] = Field(default_factory=list, description="Movie genres")
    similarity_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Cosine similarity score (higher = more similar)"
    )
    avg_rating: Optional[float] = Field(None, description="Average rating")


class SimilarMoviesResponse(BaseModel):
    """Response for similar movies endpoint."""
    movie_id: int = Field(..., description="Reference movie ID")
    title: str = Field(..., description="Reference movie title")
    n_similar: int = Field(..., description="Number of similar movies")
    similar_movies: List[SimilarMovie] = Field(
        default_factory=list,
        description="List of similar movies"
    )
    message: Optional[str] = Field(
        None,
        description="Optional message"
    )


class SimilarUser(BaseModel):
    """Similar user result."""
    user_id: int = Field(..., description="Similar user ID")
    similarity_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Cosine similarity score"
    )
    common_ratings: int = Field(
        ...,
        description="Number of movies both users have rated"
    )
    top_common_genres: List[str] = Field(
        default_factory=list,
        description="Genres both users frequently rate highly"
    )


class SimilarUsersResponse(BaseModel):
    """Response for similar users endpoint."""
    user_id: int = Field(..., description="Reference user ID")
    n_similar: int = Field(..., description="Number of similar users")
    similar_users: List[SimilarUser] = Field(
        default_factory=list,
        description="List of similar users"
    )
    message: Optional[str] = Field(
        None,
        description="Optional message"
    )


# ============================================================
# BATCH MODELS (Future use)
# ============================================================

class BatchRecommendationItem(BaseModel):
    """Single item in batch recommendation."""
    user_id: int = Field(..., description="User ID")
    recommendations: List[MovieRecommendation] = Field(
        default_factory=list,
        description="User's recommendations"
    )


class BatchRecommendationResponse(BaseModel):
    """Response for batch recommendations (future feature)."""
    n_users: int = Field(..., description="Number of users processed")
    results: List[BatchRecommendationItem] = Field(
        default_factory=list,
        description="Recommendations for each user"
    )
    processing_time_ms: Optional[float] = Field(
        None,
        description="Total processing time"
    )
