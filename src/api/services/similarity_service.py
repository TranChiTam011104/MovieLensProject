"""
Similarity Service - Compute item-item and user-user similarity.

CHỨC NĂNG:
- get_similar_movies(): Tìm phim tương tự (Item-based CF)
- get_similar_users(): Tìm users tương tự (User-based CF)

THUẬT TOÁN:
- Cosine Similarity trên SVD latent factors
- similarity(a, b) = cos(θ) = (a · b) / (||a|| × ||b||)
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
import pandas as pd
from pathlib import Path

# ML imports
from sklearn.metrics.pairwise import cosine_similarity

# Config
from ...utils.config import MODELS_DIR, MODEL_FILENAMES, MODEL_NAME


class SimilarityService:
    """
    Service for computing item-item and user-user similarity.
    
    Sử dụng SVD latent factors để compute similarity:
    - Item similarity: dựa trên movie embeddings (q_i)
    - User similarity: dựa trên user embeddings (p_u)
    """
    
    def __init__(self, model_path: Path = None, model_name: str = None):
        """
        Initialize similarity service.
        
        ARGS:
            model_path: Path to trained SVD model.
            model_name: Name for model file (without .pkl extension).
        """
        self._model_name = model_name or MODEL_NAME
        self.model_path = model_path or (MODELS_DIR / f"{self._model_name}.pkl")
        self.model = None
        self._is_loaded = False
        
        # Latent factor matrices
        self._user_factors = None  # p_u: (n_users, n_factors)
        self._item_factors = None  # q_i: (n_items, n_factors)
        self._user_id_map = None   # external -> internal
        self._item_id_map = None   # external -> internal
        
        # Data caches
        self._ratings_df = None
        self._movies_df = None
        self._trainset = None
        
    def load_model(self) -> bool:
        """
        Load trained SVD model and extract latent factors.
        
        RETURNS:
            True if loaded successfully, False otherwise.
        """
        try:
            import joblib
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                self._is_loaded = True
                print(f"✅ SimilarityService: Model loaded from {self.model_path}")
                return True
            else:
                print(f"⚠️ SimilarityService: Model file not found: {self.model_path}")
                return False
        except Exception as e:
            print(f"❌ SimilarityService: Failed to load model: {e}")
            return False
    
    def set_data(
        self,
        ratings_df: pd.DataFrame,
        movies_df: pd.DataFrame,
        trainset=None
    ):
        """
        Set dataframes for similarity computation.
        
        ARGS:
            ratings_df: DataFrame with columns [user_id, item_id, rating]
            movies_df: DataFrame with movie metadata
            trainset: Optional Surprise trainset for ID mapping
        """
        self._ratings_df = ratings_df
        self._movies_df = movies_df
        self._trainset = trainset
        
        if self.model is not None and trainset is not None:
            self._extract_latent_factors()
    
    def _extract_latent_factors(self):
        """Extract and cache latent factors from the model."""
        if self.model is None or self._trainset is None:
            return
        
        # User factors (pu) - shape: (n_users, n_factors)
        if hasattr(self.model, 'pu'):
            # pu is already in correct shape
            self._user_factors = self.model.pu
            
        # Item factors (qi) - shape: (n_items, n_factors)
        if hasattr(self.model, 'qi'):
            self._item_factors = self.model.qi
        
        # Create ID mappings (Surprise uses internal IDs)
        if self._trainset:
            # Build mappings
            all_users = list(self._trainset.all_users())
            all_items = list(self._trainset.all_items())
            
            self._user_id_map = {
                self._trainset.to_raw_uid(uid): idx 
                for idx, uid in enumerate(all_users)
            }
            self._item_id_map = {
                self._trainset.to_raw_iid(iid): idx 
                for idx, iid in enumerate(all_items)
            }
    
    def train_with_data(
        self,
        ratings_df: pd.DataFrame,
        movies_df: pd.DataFrame,
        n_factors: int = 100,
        n_epochs: int = 20
    ) -> 'SimilarityService':
        """
        Train model and prepare for similarity computation.
        
        ARGS:
            ratings_df: DataFrame with columns [user_id, item_id, rating]
            movies_df: DataFrame with movie metadata
            n_factors: Number of latent factors
            n_epochs: Number of training epochs
            
        RETURNS:
            self (for chaining)
        """
        from surprise import SVD, Dataset, Reader
        
        # Prepare data
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(ratings_df[['user_id', 'item_id', 'rating']], reader)
        trainset = data.build_full_trainset()
        
        # Train model
        self.model = SVD(
            n_factors=n_factors,
            n_epochs=n_epochs,
            lr_all=0.005,
            reg_all=0.02,
            random_state=42
        )
        self.model.fit(trainset)
        
        # Store data and extract factors
        self._ratings_df = ratings_df
        self._movies_df = movies_df
        self._trainset = trainset
        self._extract_latent_factors()
        self._is_loaded = True
        
        return self
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded and (self.model is not None or self._item_factors is not None)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.
        
        ARGS:
            vec1, vec2: 1D numpy arrays
            
        RETURNS:
            Cosine similarity (0-1)
        """
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def get_similar_movies(
        self,
        movie_id: int,
        n: int = 10,
        min_similarity: float = 0,
        use_surprise_ids: bool = False
    ) -> List[Dict]:
        """
        Find movies similar to the given movie.
        
        Uses Item-based Collaborative Filtering on SVD latent factors.
        
        ARGS:
            movie_id: Reference movie ID
            n: Number of similar movies to return
            min_similarity: Minimum similarity threshold (0-1)
            use_surprise_ids: If True, movie_id is internal Surprise ID
            
        RETURNS:
            List of dicts with movie_id, title, similarity_score, etc.
        """
        if not self.is_loaded or self._item_factors is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Get item index
        if use_surprise_ids:
            item_idx = movie_id
        else:
            # Convert external ID to internal index
            if self._item_id_map is None:
                # Fallback: assume sequential IDs starting from 0
                item_idx = movie_id - 1  # MovieLens IDs start from 1
            else:
                if movie_id not in self._item_id_map:
                    return []
                item_idx = self._item_id_map[movie_id]
        
        # Get reference movie's factor vector
        try:
            ref_vector = self._item_factors[item_idx]
        except IndexError:
            return []
        
        # Compute similarity with all other movies
        similarities = []
        n_items = self._item_factors.shape[0]
        
        for idx in range(n_items):
            if idx == item_idx:
                continue
            
            sim = self._cosine_similarity(ref_vector, self._item_factors[idx])
            if sim >= min_similarity:
                # Convert index back to movie_id
                if self._trainset:
                    raw_movie_id = self._trainset.to_raw_iid(idx)
                else:
                    raw_movie_id = idx + 1  # Fallback
                    
                similarities.append({
                    'movie_id': raw_movie_id,
                    'similarity_score': sim,
                    'index': idx
                })
        
        # Sort by similarity (descending) and take top-N
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_similar = similarities[:n]
        
        # Add movie metadata
        if self._movies_df is not None:
            movie_dict = self._movies_df.set_index('movie_id').to_dict('index')
            for item in top_similar:
                mid = item['movie_id']
                if mid in movie_dict:
                    item['title'] = movie_dict[mid].get('title', 'Unknown')
                    item['genres'] = movie_dict[mid].get('genres', [])
                    item['avg_rating'] = movie_dict[mid].get('avg_rating')
                # Remove internal index
                del item['index']
        
        return top_similar
    
    def get_similar_users(
        self,
        user_id: int,
        n: int = 10,
        min_similarity: float = 0
    ) -> List[Dict]:
        """
        Find users similar to the given user.
        
        Uses User-based Collaborative Filtering on SVD latent factors.
        
        ARGS:
            user_id: Reference user ID
            n: Number of similar users to return
            min_similarity: Minimum similarity threshold (0-1)
            
        RETURNS:
            List of dicts with user_id, similarity_score, common_ratings, etc.
        """
        if not self.is_loaded or self._user_factors is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Get user index
        if self._user_id_map is None:
            user_idx = user_id - 1  # Fallback: assume sequential IDs
        else:
            if user_id not in self._user_id_map:
                return []
            user_idx = self._user_id_map[user_id]
        
        # Get reference user's factor vector
        try:
            ref_vector = self._user_factors[user_idx]
        except IndexError:
            return []
        
        # Compute similarity with all other users
        similarities = []
        n_users = self._user_factors.shape[0]
        
        for idx in range(n_users):
            if idx == user_idx:
                continue
            
            sim = self._cosine_similarity(ref_vector, self._user_factors[idx])
            if sim >= min_similarity:
                # Convert index back to user_id
                if self._trainset:
                    raw_user_id = self._trainset.to_raw_uid(idx)
                else:
                    raw_user_id = idx + 1
                    
                similarities.append({
                    'user_id': raw_user_id,
                    'similarity_score': sim,
                    'index': idx
                })
        
        # Sort by similarity and take top-N
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_similar = similarities[:n]
        
        # Add additional info (common ratings, genres)
        if self._ratings_df is not None:
            # Get reference user's ratings
            ref_ratings = self._ratings_df[self._ratings_df['user_id'] == user_id]
            ref_movies = set(ref_ratings['item_id'].tolist())
            
            for item in top_similar:
                other_user_id = item['user_id']
                
                # Count common ratings
                other_ratings = self._ratings_df[self._ratings_df['user_id'] == other_user_id]
                other_movies = set(other_ratings['item_id'].tolist())
                common_count = len(ref_movies & other_movies)
                
                item['common_ratings'] = common_count
                
                # Find top common genres
                if self._movies_df is not None and common_count > 0:
                    common_movie_ids = ref_movies & other_movies
                    common_genres = self._get_common_genres(
                        list(common_movie_ids),
                        ref_ratings
                    )
                    item['top_common_genres'] = common_genres
                
                del item['index']
        
        return top_similar
    
    def _get_common_genres(
        self,
        movie_ids: List[int],
        ratings_df: pd.DataFrame
    ) -> List[str]:
        """
        Get top genres from user's highly-rated movies.
        
        ARGS:
            movie_ids: List of movie IDs
            ratings_df: Reference user's ratings DataFrame
            
        RETURNS:
            List of top genre names
        """
        if self._movies_df is None:
            return []
        
        # Filter movies and join with ratings
        movies = self._movies_df[self._movies_df['movie_id'].isin(movie_ids)]
        
        # Get user's ratings for these movies
        user_ratings = ratings_df[ratings_df['item_id'].isin(movie_ids)]
        
        # Merge to get ratings per movie
        movies_with_ratings = movies.merge(
            user_ratings[['item_id', 'rating']],
            left_on='movie_id',
            right_on='item_id'
        )
        
        # Filter highly rated (>= 4)
        high_rated = movies_with_ratings[movies_with_ratings['rating'] >= 4]
        
        # Count genres
        genre_counts = {}
        for genres in high_rated['genres']:
            for genre in genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # Sort and return top 3
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        return [g[0] for g in sorted_genres[:3]]
    
    def batch_compute_similar_movies(
        self,
        movie_ids: List[int],
        n: int = 10
    ) -> Dict[int, List[Dict]]:
        """
        Compute similar movies for multiple movies at once.
        
        More efficient than calling get_similar_movies multiple times.
        
        RETURNS:
            Dict mapping movie_id -> list of similar movies
        """
        if not self.is_loaded or self._item_factors is None:
            raise RuntimeError("Model not loaded.")
        
        results = {}
        for movie_id in movie_ids:
            results[movie_id] = self.get_similar_movies(movie_id, n=n)
        
        return results


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_similarity_service: Optional[SimilarityService] = None


def get_similarity_service(model_name: str = None) -> SimilarityService:
    """Get or create global similarity service."""
    global _similarity_service
    if _similarity_service is None:
        _similarity_service = SimilarityService(model_name=model_name)
    return _similarity_service


def load_similarity_service(model_path: Path = None, model_name: str = None) -> bool:
    """Load the global similarity service."""
    global _similarity_service
    if _similarity_service is None:
        _similarity_service = SimilarityService(model_path=model_path, model_name=model_name)
    return _similarity_service.load_model()
