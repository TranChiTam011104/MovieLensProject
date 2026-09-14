"""
ML Recommendation Engine - Core ML logic cho recommendations.

CHỨC NĂNG:
- predict_rating(): Dự đoán rating cho user-movie pair
- get_recommendations(): Lấy top-N recommendations cho user

THUẬT TOÁN: SVD (Singular Value Decomposition)
- Matrix Factorization: r_ui = μ + b_u + b_i + p_u.q_i
- User và Movie được embed vào latent space
- Similarity computed bằng cosine similarity
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
import pandas as pd
from pathlib import Path
import os

# ML imports
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split

# Config
from ...utils.config import MODELS_DIR, MODEL_FILENAMES


class RecommendationEngine:
    """
    SVD-based Recommendation Engine.
    
    Sử dụng SVD (Singular Value Decomposition) để:
    1. Predict ratings cho user-movie pairs
    2. Generate personalized recommendations
    3. Compute item/user similarities
    """
    
    def __init__(self, model_path: Path = None):
        """
        Initialize recommendation engine.
        
        ARGS:
            model_path: Path to trained SVD model. If None, uses default path.
        """
        self.model = None
        self.model_path = model_path or (MODELS_DIR / MODEL_FILENAMES["svd"])
        self._is_loaded = False
        
        # Data caches
        self._ratings_df = None
        self._movies_df = None
        self._user_factors = None
        self._item_factors = None
        
    def load_model(self) -> bool:
        """
        Load trained SVD model from disk.
        
        RETURNS:
            True if loaded successfully, False otherwise.
        """
        try:
            import joblib
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                self._is_loaded = True
                print(f"✅ Model loaded from {self.model_path}")
                return True
            else:
                print(f"⚠️ Model file not found: {self.model_path}")
                return False
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False
    
    def train(self, ratings_df: pd.DataFrame, n_factors: int = 100, n_epochs: int = 20) -> 'RecommendationEngine':
        """
        Train SVD model on ratings data.
        
        ARGS:
            ratings_df: DataFrame with columns [user_id, item_id, rating]
            n_factors: Number of latent factors
            n_epochs: Number of training epochs
            
        RETURNS:
            self (for chaining)
        """
        # Prepare data for Surprise
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(ratings_df[['user_id', 'item_id', 'rating']], reader)
        
        # Build full trainset
        trainset = data.build_full_trainset()
        
        # Train SVD
        self.model = SVD(
            n_factors=n_factors,
            n_epochs=n_epochs,
            lr_all=0.005,
            reg_all=0.02,
            random_state=42
        )
        self.model.fit(trainset)
        
        # Cache latent factors for similarity computation
        self._user_factors = trainset.build_testset()
        self._user_factors = {
            u: self.model.pu[trainset.to_inner_uid(u)]
            for u in trainset.all_users()
        } if hasattr(self.model, 'pu') else None
        self._item_factors = {
            i: self.model.qi[trainset.to_inner_iid(i)]
            for i in trainset.all_items()
        } if hasattr(self.model, 'qi') else None
        
        self._is_loaded = True
        
        # Save model
        import joblib
        os.makedirs(self.model_path.parent, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"✅ Model trained and saved to {self.model_path}")
        
        return self
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded and self.model is not None
    
    def predict_rating(self, user_id: int, movie_id: int) -> Tuple[float, float]:
        """
        Predict rating for a user-movie pair.
        
        ARGS:
            user_id: User ID
            movie_id: Movie ID
            
        RETURNS:
            Tuple of (predicted_rating, confidence)
            - confidence is estimated based on number of ratings
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() or train() first.")
        
        # Predict using SVD
        prediction = self.model.predict(user_id, movie_id)
        
        # Estimate confidence (higher if user/item has more ratings)
        # Simplified: use prediction.est as confidence proxy
        # More sophisticated: compute based on variance of predictions
        confidence = min(1.0, 0.5 + 0.1 * len(prediction.details)) if hasattr(prediction, 'details') else 0.8
        
        return prediction.est, confidence
    
    def get_recommendations(
        self,
        user_id: int,
        n: int = 10,
        exclude_watched: bool = True,
        min_rating: float = 0,
        ratings_df: pd.DataFrame = None,
        movies_df: pd.DataFrame = None
    ) -> List[Dict]:
        """
        Get top-N movie recommendations for a user.
        
        ARGS:
            user_id: User ID
            n: Number of recommendations
            exclude_watched: Exclude movies user has already rated
            min_rating: Minimum predicted rating threshold
            ratings_df: DataFrame of ratings (for exclude_watched)
            movies_df: DataFrame of movies (for metadata)
            
        RETURNS:
            List of dicts with movie_id, title, predicted_rating, etc.
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() or train() first.")
        
        # Use cached data if not provided
        if movies_df is None:
            movies_df = self._movies_df
        if ratings_df is None:
            ratings_df = self._ratings_df
        
        # Get all movie IDs
        if movies_df is not None:
            all_movie_ids = movies_df['movie_id'].unique().tolist()
        else:
            # If no movies_df, try to get from training data
            all_movie_ids = list(range(1, 1683))  # MovieLens 100K has 1682 movies
        
        # Exclude watched movies if ratings_df provided
        if exclude_watched and ratings_df is not None:
            watched_movies = ratings_df[ratings_df['user_id'] == user_id]['item_id'].unique()
            all_movie_ids = [m for m in all_movie_ids if m not in watched_movies]
        
        # Predict ratings for all candidate movies
        predictions = []
        for movie_id in all_movie_ids:
            pred_rating, confidence = self.predict_rating(user_id, movie_id)
            if pred_rating >= min_rating:
                predictions.append({
                    'movie_id': movie_id,
                    'predicted_rating': pred_rating,
                    'confidence': confidence
                })
        
        # Sort by predicted rating (descending)
        predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
        
        # Take top-N
        top_predictions = predictions[:n]
        
        # Add movie metadata if movies_df provided
        if movies_df is not None:
            movie_dict = movies_df.set_index('movie_id').to_dict('index')
            for pred in top_predictions:
                mid = pred['movie_id']
                if mid in movie_dict:
                    pred['title'] = movie_dict[mid].get('title', 'Unknown')
                    pred['genres'] = movie_dict[mid].get('genres', [])
        
        return top_predictions
    
    def save_model(self, path: Path = None):
        """Save model to disk."""
        import joblib
        path = path or self.model_path
        os.makedirs(path.parent, exist_ok=True)
        joblib.dump(self.model, path)
        print(f"✅ Model saved to {path}")
    
    def get_user_factor(self, user_id: int) -> Optional[np.ndarray]:
        """
        Get user's latent factor vector from SVD.
        
        ARGS:
            user_id: User ID
            
        RETURNS:
            numpy array of latent factors, or None if not available
        """
        if not self.is_loaded or not hasattr(self.model, 'pu'):
            return None
        
        try:
            # Surprise uses internal IDs, need to convert
            # This requires access to trainset - simplified version
            return None
        except:
            return None
    
    def get_item_factor(self, movie_id: int) -> Optional[np.ndarray]:
        """
        Get movie's latent factor vector from SVD.
        
        ARGS:
            movie_id: Movie ID
            
        RETURNS:
            numpy array of latent factors, or None if not available
        """
        if not self.is_loaded or not hasattr(self.model, 'qi'):
            return None
        return None


# ============================================================
# SINGLETON INSTANCE (for app-wide use)
# ============================================================

# Global engine instance - lazy loaded
_engine: Optional[RecommendationEngine] = None


def get_engine() -> RecommendationEngine:
    """
    Get or create global recommendation engine.
    
    RETURNS:
        RecommendationEngine singleton
    """
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
    return _engine


def load_engine(model_path: Path = None) -> bool:
    """
    Load the global recommendation engine.
    
    RETURNS:
        True if loaded successfully
    """
    global _engine
    if _engine is None:
        _engine = RecommendationEngine(model_path)
    return _engine.load_model()


def train_engine(ratings_df: pd.DataFrame, **kwargs) -> RecommendationEngine:
    """
    Train and set global recommendation engine.
    
    RETURNS:
        Trained RecommendationEngine
    """
    global _engine
    _engine = RecommendationEngine()
    return _engine.train(ratings_df, **kwargs)
