"""
Shared utilities for API endpoints.
"""
import pandas as pd
from pathlib import Path
from ..utils.config import RAW_DATA_DIR, RATINGS_FILE, RATINGS_COLUMNS

# Cache tất cả ratings từ data gốc (u.data)
_all_ratings_df: pd.DataFrame = None


def get_all_ratings() -> pd.DataFrame:
    """
    Load tất cả ratings từ u.data (lazy load, cached).
    
    Returns:
        DataFrame với columns: user_id, item_id, rating
    """
    global _all_ratings_df
    if _all_ratings_df is None:
        ratings_path = Path(RAW_DATA_DIR) / RATINGS_FILE
        _all_ratings_df = pd.read_csv(
            ratings_path,
            sep='\t',
            names=RATINGS_COLUMNS,
            usecols=['user_id', 'item_id', 'rating']
        )
    return _all_ratings_df


def get_actual_rating(user_id: int, movie_id: int, ratings_df: pd.DataFrame = None) -> float | None:
    """
    Get actual rating for a user-movie pair.
    
    Args:
        user_id: User ID
        movie_id: Movie ID  
        ratings_df: Optional pre-loaded ratings DataFrame
        
    Returns:
        Rating as float, or None if not found
    """
    if ratings_df is None:
        ratings_df = get_all_ratings()
    
    user_movie = ratings_df[
        (ratings_df['user_id'] == user_id) & 
        (ratings_df['item_id'] == movie_id)
    ]
    
    if user_movie.empty:
        return None
    
    return round(float(user_movie.iloc[0]['rating']), 2)
