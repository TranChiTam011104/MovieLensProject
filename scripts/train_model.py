"""
Script để train và lưu SVD model.

CHẠY:
    python scripts/train_model.py

OUTPUT:
    models/svd_model.pkl - Trained SVD model
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import joblib
from surprise import SVD, Dataset, Reader
import time

# Import project modules
from src.data.load import load_ratings, load_movies
from src.data.preprocess import process_movies, add_rating_stats
from src.utils.config import MODELS_DIR, MODEL_FILENAMES


def train_svd_model(
    n_factors: int = 100,
    n_epochs: int = 20,
    lr_all: float = 0.005,
    reg_all: float = 0.02,
    random_state: int = 42
):
    """
    Train SVD model on MovieLens 100K dataset.
    
    ARGS:
        n_factors: Number of latent factors
        n_epochs: Number of training epochs
        lr_all: Learning rate
        reg_all: Regularization strength
        random_state: Random seed
        
    RETURNS:
        Trained SVD model
    """
    print("=" * 60)
    print("🎬 MovieLens SVD Model Training")
    print("=" * 60)
    
    # Load data
    print("\n📂 Loading data...")
    start_time = time.time()
    
    ratings_df = load_ratings()
    movies_df = load_movies()
    processed_movies = process_movies(movies_df)
    processed_movies = add_rating_stats(processed_movies, ratings_df)
    
    print(f"   ✓ Loaded {len(ratings_df):,} ratings")
    print(f"   ✓ Loaded {len(processed_movies):,} movies")
    print(f"   ⏱️ Data loading: {time.time() - start_time:.2f}s")
    
    # Prepare for Surprise
    print("\n🔧 Preparing data for SVD...")
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(
        ratings_df[['user_id', 'item_id', 'rating']], 
        reader
    )
    
    # Build trainset (use all data for training)
    trainset = data.build_full_trainset()
    
    print(f"   ✓ Trainset: {trainset.n_users:,} users, {trainset.n_items:,} items, {trainset.n_ratings:,} ratings")
    
    # Train model
    print(f"\n🤖 Training SVD model...")
    print(f"   Parameters: n_factors={n_factors}, n_epochs={n_epochs}")
    print(f"   Learning rate: {lr_all}, Regularization: {reg_all}")
    
    start_time = time.time()
    
    model = SVD(
        n_factors=n_factors,
        n_epochs=n_epochs,
        lr_all=lr_all,
        reg_all=reg_all,
        random_state=random_state
    )
    
    model.fit(trainset)
    
    train_time = time.time() - start_time
    print(f"   ✓ Training completed in {train_time:.2f}s")
    
    # Save model
    print("\n💾 Saving model...")
    model_path = MODELS_DIR / MODEL_FILENAMES["svd"]
    joblib.dump(model, model_path)
    print(f"   ✓ Model saved to: {model_path}")
    
    # Quick evaluation on training data
    print("\n📊 Quick evaluation on training data...")
    predictions = model.test(trainset.build_testset())
    
    from surprise.accuracy import rmse, mae
    train_rmse = rmse(predictions)
    train_mae = mae(predictions)
    
    print(f"   Training RMSE: {train_rmse:.4f}")
    print(f"   Training MAE:  {train_mae:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print("=" * 60)
    
    return model


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train SVD model")
    parser.add_argument("--factors", type=int, default=100, help="Number of latent factors")
    parser.add_argument("--epochs", type=int, default=20, help="Number of epochs")
    parser.add_argument("--lr", type=float, default=0.005, help="Learning rate")
    parser.add_argument("--reg", type=float, default=0.02, help="Regularization")
    
    args = parser.parse_args()
    
    train_svd_model(
        n_factors=args.factors,
        n_epochs=args.epochs,
        lr_all=args.lr,
        reg_all=args.reg
    )
