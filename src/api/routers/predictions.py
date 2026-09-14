"""
Predictions Router - Endpoints for rating predictions.

ENDPOINTS:
- GET /v1/predict/{user_id}/{movie_id} - Predict rating for user-movie pair
"""

from fastapi import APIRouter, HTTPException, Path

# Import models
from ..models import (
    PredictionResponse,
    ErrorResponse
)

# Import services
from ..services.recommendation_engine import get_engine

router = APIRouter(prefix="/v1", tags=["Predictions"])


@router.get(
    "/predict/users/{user_id}/movies/{movie_id}",
    response_model=PredictionResponse,
    responses={
        404: {"model": ErrorResponse}
    }
)
async def predict_rating(
    user_id: int = Path(..., ge=1, le=943, description="User ID (1-943)"),
    movie_id: int = Path(..., ge=1, description="Movie ID")
):
    """
    Predict how a user would rate a specific movie.
    
    Uses **SVD (Singular Value Decomposition)** to predict the rating.
    
    **Prediction formula**:
    ```
    predicted_rating = μ + b_u + b_i + p_u · q_i
    
    Where:
    - μ: global mean rating
    - b_u: user bias (tendency to rate high/low)
    - b_i: item bias (tendency to be rated high/low)
    - p_u: user latent factors
    - q_i: item latent factors
    ```
    
    **Use cases**:
    - Movie detail page: "You'd rate this 4.5 stars"
    - Decision engine: Should we recommend this movie?
    - A/B testing: Compare predicted vs actual ratings
    - Quality assessment: Is our model accurate?
    """
    # Get engine
    engine = get_engine()
    
    # Check if model is loaded
    if not engine.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please wait for initialization."
        )
    
    # Validate user exists
    if user_id < 1 or user_id > 943:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} does not exist"
        )
    
    try:
        # Predict rating
        predicted_rating, confidence = engine.predict_rating(user_id, movie_id)
        
        return PredictionResponse(
            user_id=user_id,
            movie_id=movie_id,
            predicted_rating=round(predicted_rating, 2),
            confidence=round(confidence, 2),
            actual_rating=None  # Would need to query DB for actual rating
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting rating: {str(e)}"
        )
