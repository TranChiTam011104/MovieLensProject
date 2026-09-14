"""
MovieLens Recommendation API - Main FastAPI Application.

Một REST API cho movie recommendations dựa trên SVD collaborative filtering.

FEATURES:
- Personalized recommendations
- Rating predictions
- Similar movies (Item-based CF)
- Similar users (User-based CF)
- Movie metadata

USAGE:
    # Development
    uvicorn src.api.main:app --reload
    
    # Production
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000

DOCS:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - OpenAPI: http://localhost:8000/openapi.json
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================
# APP LIFECYCLE - Load/unload models
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    """
    # STARTUP
    logger.info("🚀 Starting MovieLens Recommendation API...")
    
    try:
        # Import services
        from src.api.services.recommendation_engine import get_engine, load_engine
        from src.api.services.similarity_service import get_similarity_service
        
        # Import data loaders
        from src.data.load import load_ratings, load_movies
        from src.data.preprocess import process_movies, add_rating_stats
        
        # Load data first
        logger.info("📂 Loading data...")
        ratings_df = load_ratings()
        movies_df = load_movies()
        processed_movies = process_movies(movies_df)
        processed_movies = add_rating_stats(processed_movies, ratings_df)
        
        logger.info(f"   ✓ Loaded {len(ratings_df)} ratings")
        logger.info(f"   ✓ Loaded {len(processed_movies)} movies")
        
        # Try to load pre-trained model
        logger.info("🤖 Loading SVD model...")
        model_loaded = load_engine()
        
        if not model_loaded:
            # Train model if not found
            logger.info("⚠️ Model not found, training new model...")
            
            from surprise import Dataset, Reader
            
            engine = get_engine()
            reader = Reader(rating_scale=(1, 5))
            data = Dataset.load_from_df(
                ratings_df[['user_id', 'item_id', 'rating']], 
                reader
            )
            trainset = data.build_full_trainset()
            
            engine.train(ratings_df, n_factors=100, n_epochs=20)
            
            # Also train similarity service
            sim_service = get_similarity_service()
            sim_service.train_with_data(
                ratings_df=ratings_df,
                movies_df=processed_movies,
                n_factors=100,
                n_epochs=20
            )
            
            # Load trained similarity service factors
            sim_service._ratings_df = ratings_df
            sim_service._movies_df = processed_movies
            sim_service._trainset = trainset
            sim_service._extract_latent_factors()
        else:
            # Initialize similarity service with loaded model
            logger.info("🔗 Initializing similarity service...")
            from src.api.services.recommendation_engine import get_engine
            
            sim_service = get_similarity_service()
            
            from surprise import Dataset, Reader
            reader = Reader(rating_scale=(1, 5))
            data = Dataset.load_from_df(
                ratings_df[['user_id', 'item_id', 'rating']], 
                reader
            )
            trainset = data.build_full_trainset()
            
            # Load the model into similarity service
            engine = get_engine()
            sim_service.model = engine.model
            sim_service._ratings_df = ratings_df
            sim_service._movies_df = processed_movies
            sim_service._trainset = trainset
            sim_service._extract_latent_factors()
            sim_service._is_loaded = True
        
        # Cache movies
        from src.api.routers import movies as movies_module
        movies_module._movies_cache = {
            row['movie_id']: row.to_dict()
            for _, row in processed_movies.iterrows()
        }
        
        logger.info("✅ API ready!")
        logger.info("📖 Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
    
    yield
    
    # SHUTDOWN
    logger.info("👋 Shutting down MovieLens Recommendation API...")
    
    # Cleanup
    from src.api.routers import movies as movies_module
    movies_module._movies_cache = None


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="MovieLens Recommendation API",
    description="""
## Overview

API for movie recommendations based on **SVD Collaborative Filtering**.

## Features

- **Personalized Recommendations**: Get movies tailored to each user's taste
- **Rating Predictions**: Predict how a user would rate any movie
- **Similar Movies**: Find movies similar to a given movie (Item-based CF)
- **Similar Users**: Find users with similar preferences (User-based CF)
- **Movie Metadata**: Browse movie information

## Algorithm

Uses **SVD (Singular Value Decomposition)** matrix factorization:

```
predicted_rating = μ + b_u + b_i + p_u · q_i

Where:
- μ: global mean rating
- b_u: user bias
- b_i: item bias
- p_u: user latent factors
- q_i: item latent factors
```

## Authentication

Currently no authentication (for internal use).
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ============================================================
# MIDDLEWARE
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# INCLUDE ROUTERS
# ============================================================

from src.api.routers import health, recommendations, predictions, movies

app.include_router(health.router)
app.include_router(recommendations.router)
app.include_router(predictions.router)
app.include_router(movies.router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "name": "MovieLens Recommendation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================================
# MAIN - Run directly
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                               ║
║   🎬 MovieLens Recommendation API                            ║
║                                                               ║
║   📖 Swagger UI:      http://localhost:8000/docs              ║
║   📚 ReDoc:          http://localhost:8000/redoc              ║
║   🏥 Health:        http://localhost:8000/health             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
