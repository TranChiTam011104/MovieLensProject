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
import pandas as pd

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
        from src.data.load import load_ratings, load_movies, load_train_test_data
        from src.data.preprocess import process_movies, add_rating_stats
        from src.utils.config import (
            N_FACTORS, N_EPOCHS, 
            SIM_N_FACTORS, SIM_N_EPOCHS, DEFAULT_N_RECOMMENDATIONS,
            TOTAL_USERS, TOTAL_MOVIES, MODEL_NAME,
            get_fold_from_model_name, get_train_test_files_from_model_name
        )
        
        # Xác định fold từ model_name
        model_fold = get_fold_from_model_name(MODEL_NAME)
        train_file, test_file, is_full_data = get_train_test_files_from_model_name(MODEL_NAME)
        
        logger.info(f"📂 Loading data for model: {MODEL_NAME}")
        logger.info(f"   Fold: {model_fold}, Train file: {train_file}, Full data: {is_full_data}")
        
        # Load train/test data dựa trên model_name
        train_df, test_df = load_train_test_data(model_name=MODEL_NAME)
        logger.info(f"   ✓ Train: {len(train_df)} ratings")
        if test_df is not None:
            logger.info(f"   ✓ Test: {len(test_df)} ratings")
        else:
            logger.info(f"   ✓ Using full data (no test split)")
        
        # Load movies
        movies_df = load_movies()
        processed_movies = process_movies(movies_df)
        
        # For recommendations: use train_df + test_df combined for stats
        # (vì khi recommend, cần biết tổng quan về user/item)
        if test_df is not None:
            all_ratings_df = pd.concat([train_df, test_df], ignore_index=True)
        else:
            all_ratings_df = train_df
        processed_movies = add_rating_stats(processed_movies, all_ratings_df)
        
        # Try to load pre-trained model
        logger.info(f"🤖 Loading SVD model: {MODEL_NAME}...")
        model_loaded = load_engine(model_name=MODEL_NAME)
        
        if not model_loaded:
            # Train model if not found (train trên train_df)
            logger.info("⚠️ Model not found, training new model...")
            
            from surprise import Dataset, Reader
            
            engine = get_engine(model_name=MODEL_NAME)
            reader = Reader(rating_scale=(1, 5))
            data = Dataset.load_from_df(
                train_df[['user_id', 'item_id', 'rating']], 
                reader
            )
            trainset = data.build_full_trainset()
            
            # Train model trên train_df
            engine.train(train_df, n_factors=N_FACTORS, n_epochs=N_EPOCHS)
            
            # Also train similarity service
            sim_service = get_similarity_service(model_name=MODEL_NAME)
            sim_service.train_with_data(
                ratings_df=train_df,
                movies_df=processed_movies,
                n_factors=SIM_N_FACTORS,
                n_epochs=SIM_N_EPOCHS
            )
            
            # Load trained similarity service factors
            sim_service._ratings_df = train_df
            sim_service._movies_df = processed_movies
            sim_service._trainset = trainset
            sim_service._extract_latent_factors()

            # Cache data for recommendation engine
            # Dùng train_df cho model, all_ratings_df cho stats
            engine = get_engine(model_name=MODEL_NAME)
            engine._ratings_df = train_df
            engine._movies_df = processed_movies
        else:
            # Initialize similarity service with loaded model
            logger.info("🔗 Initializing similarity service...")
            from src.api.services.recommendation_engine import get_engine
            
            sim_service = get_similarity_service(model_name=MODEL_NAME)
            
            from surprise import Dataset, Reader
            reader = Reader(rating_scale=(1, 5))
            data = Dataset.load_from_df(
                train_df[['user_id', 'item_id', 'rating']], 
                reader
            )
            trainset = data.build_full_trainset()
            
            # Load the model into similarity service
            engine = get_engine(model_name=MODEL_NAME)
            sim_service.model = engine.model
            sim_service._ratings_df = train_df
            sim_service._movies_df = processed_movies
            sim_service._trainset = trainset
            sim_service._extract_latent_factors()
            sim_service._is_loaded = True

            # Cache data for recommendation engine
            engine._ratings_df = train_df
            engine._movies_df = processed_movies
        
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

from src.api.routers import health, recommendations, predictions, movies, registry

app.include_router(health.router)
app.include_router(recommendations.router)
app.include_router(predictions.router)
app.include_router(movies.router)
app.include_router(registry.router)


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


@app.get("/model-info", tags=["Model"])
async def model_info():
    """
    Get current model configuration and info.
    """
    from src.utils.config import (
        N_FACTORS, N_EPOCHS, MODEL_NAME,
        TOTAL_USERS, TOTAL_MOVIES, SIM_N_FACTORS, SIM_N_EPOCHS,
        get_fold_from_model_name, get_train_test_files_from_model_name
    )
    
    # Get engine info
    from src.api.services.recommendation_engine import get_engine
    engine = get_engine()
    
    # Xác định train/test file từ model_name
    model_fold = get_fold_from_model_name(MODEL_NAME)
    train_file, test_file, is_full_data = get_train_test_files_from_model_name(MODEL_NAME)
    
    # Get train data info
    from src.data.load import load_train_test_data
    train_df, test_df = load_train_test_data(model_name=MODEL_NAME)
    
    return {
        "model_name": MODEL_NAME,
        "model_loaded": engine.is_loaded,
        "model_path": str(engine.model_path) if engine.model_path else None,
        "config": {
            "n_factors": N_FACTORS,
            "n_epochs": N_EPOCHS,
            "train_test_fold": model_fold if model_fold > 0 else "ua/ub",
            "is_full_data": is_full_data,
            "total_users": TOTAL_USERS,
            "total_movies": TOTAL_MOVIES,
            "sim_n_factors": SIM_N_FACTORS,
            "sim_n_epochs": SIM_N_EPOCHS
        },
        "data": {
            "train_ratings": len(train_df),
            "test_ratings": len(test_df) if test_df is not None else 0,
            "train_file": train_file,
            "test_file": test_file,
            "is_full_data": is_full_data
        }
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
