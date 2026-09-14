"""
Script để train và lưu SVD model.

CHẠY:
    python scripts/train_model.py

OUTPUT:
    models/svd_model_fold{N}.pkl - Trained SVD model
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import joblib
from surprise import SVD, Dataset, Reader
from surprise.accuracy import rmse, mae
import time

# Import project modules
from src.data.load import load_train_test_data, load_ratings
from src.utils.config import MODELS_DIR, MODEL_NAME, N_FACTORS, N_EPOCHS, LEARNING_RATE, REG_ALL, TRAIN_TEST_FOLD


def train_svd_model(
    n_factors: int = N_FACTORS,
    n_epochs: int = N_EPOCHS,
    lr_all: float = LEARNING_RATE,
    reg_all: float = REG_ALL,
    random_state: int = 42
):
    """
    Train SVD model on MovieLens 100K dataset.
    
    Data source controlled by USE_FULL_DATA in .env:
        - true: use u.data (100K ratings)
        - false: use fold-based split (TRAIN_TEST_FOLD)
        
    RETURNS:
        Trained SVD model
    """
    print("=" * 60)
    print("🎬 MovieLens SVD Model Training")
    print("=" * 60)
    
    # Read USE_FULL_DATA from environment
    env_use_full = os.getenv("USE_FULL_DATA", "true").lower() == "true"
    
    # Load data
    print(f"\n📂 Loading data...")
    start_time = time.time()
    
    if env_use_full:
        # Dùng full u.data (100K ratings)
        train_df = load_ratings()
        print(f"   ✓ Full data: {len(train_df):,} ratings (u.data)")
    else:
        # Dùng fold-based split
        train_df, test_df = load_train_test_data(fold=TRAIN_TEST_FOLD)
        print(f"   ✓ Train: {len(train_df):,} ratings")
        print(f"   ✓ Test:  {len(test_df):,} ratings")
    
    print(f"   ⏱️ Data loading: {time.time() - start_time:.2f}s")
    
    # Prepare for Surprise
    print("\n🔧 Preparing data for SVD...")
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(
        train_df[['user_id', 'item_id', 'rating']], 
        reader
    )
    
    # Build trainset
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
    model_path = MODELS_DIR / f"{MODEL_NAME}.pkl"
    joblib.dump(model, model_path)
    print(f"   ✓ Model saved to: {model_path}")
    
    # Evaluate on test data (chỉ khi dùng fold-based split)
    if not env_use_full:
        print("\n📊 Evaluating on test data...")
        test_set = [(row['user_id'], row['item_id'], row['rating']) for _, row in test_df.iterrows()]
        predictions = model.test(test_set)
        test_rmse = rmse(predictions)
        test_mae = mae(predictions)
        print(f"   Test RMSE: {test_rmse:.4f}")
        print(f"   Test MAE:  {test_mae:.4f}")
    
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
    parser.add_argument("--fold", action="store_true", help="Use fold-based split instead of full data")
    
    args = parser.parse_args()
    
    # Override USE_FULL_DATA nếu dùng --fold
    if args.fold:
        os.environ["USE_FULL_DATA"] = "false"
    
    train_svd_model(
        n_factors=args.factors,
        n_epochs=args.epochs,
        lr_all=args.lr,
        reg_all=args.reg
    )
