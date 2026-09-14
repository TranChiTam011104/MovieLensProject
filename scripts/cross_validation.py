"""
Cross-Validation Script - Chạy 5-fold CV trên tất cả thuật toán.
Xuất kết quả ra JSON và CSV report.
Tự động lưu model sau khi train.
"""

import json
import csv
import pickle
from datetime import datetime
from pathlib import Path
import pandas as pd
from surprise import Dataset, Reader, SVD, KNNBasic, KNNWithMeans, BaselineOnly
from surprise.model_selection import cross_validate
import time

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "reports"
OUTPUT_DIR.mkdir(exist_ok=True)

# Thư mục lưu model
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

# 5-fold CV files
TRAIN_FILES = ["u1.base", "u2.base", "u3.base", "u4.base", "u5.base"]
TEST_FILES = ["u1.test", "u2.test", "u3.test", "u4.test", "u5.test"]

# Thuật toán
ALGORITHMS = {
    "SVD": SVD,
    # "KNNBasic": KNNBasic,
    # "KNNWithMeans": KNNWithMeans,
    # "BaselineOnly": BaselineOnly,
}

# Metrics muốn đo
METRICS = ["RMSE", "MAE", "Fit Time", "Test Time"]


def load_fold_data(fold_idx: int):
    """Load train/test data cho 1 fold."""
    train_path = DATA_DIR / TRAIN_FILES[fold_idx]
    test_path = DATA_DIR / TEST_FILES[fold_idx]
    
    # Load data
    train_df = pd.read_csv(train_path, sep="\t", names=["user_id", "item_id", "rating", "timestamp"])
    test_df = pd.read_csv(test_path, sep="\t", names=["user_id", "item_id", "rating", "timestamp"])
    
    # Reader cho Surprise
    reader = Reader(rating_scale=(1, 5))
    trainset = Dataset.load_from_df(train_df[["user_id", "item_id", "rating"]], reader).build_full_trainset()
    test_set = list(test_df[["user_id", "item_id", "rating"]].itertuples(index=False, name=None))
    
    return trainset, test_set


def save_model(algo, algo_name: str, fold_idx: int) -> Path:
    """Lưu model đã train vào file .pkl."""
    fold_num = fold_idx + 1
    # Tên file: svd_model_fold1.pkl, knnbasic_model_fold2.pkl, ...
    filename = f"{algo_name.lower()}_model_fold{fold_num}.pkl"
    filepath = MODELS_DIR / filename
    
    with open(filepath, "wb") as f:
        pickle.dump(algo, f)
    
    return filepath


def run_algorithm(algo_class, trainset, test_set, algo_name: str, fold_idx: int):
    """Chạy 1 thuật toán trên trainset, đánh giá trên test_set."""
    print(f"  Training {algo_name}...", end=" ", flush=True)
    start = time.time()
    
    algo = algo_class()
    algo.fit(trainset)
    
    fit_time = time.time() - start
    print(f"done (fit: {fit_time:.2f}s)", flush=True)
    
    # Lưu model
    model_path = save_model(algo, algo_name, fold_idx)
    print(f"  💾 Saved: {model_path.name}")
    
    # Predict trên test set
    start = time.time()
    predictions = algo.test(test_set)
    test_time = time.time() - start
    
    # Tính metrics
    from surprise import accuracy
    rmse = accuracy.rmse(predictions, verbose=False)
    mae = accuracy.mae(predictions, verbose=False)
    
    return {
        "RMSE": rmse,
        "MAE": mae,
        "Fit Time": fit_time,
        "Test Time": test_time,
        "model_path": str(model_path),
    }


def run_cv():
    """Chạy full 5-fold cross-validation."""
    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "n_folds": 5,
            "train_files": TRAIN_FILES,
            "test_files": TEST_FILES,
            "algorithms": list(ALGORITHMS.keys()),
        },
        "per_fold": {},
        "summary": {},
    }
    
    for algo_name, algo_class in ALGORITHMS.items():
        print(f"\n{'='*50}")
        print(f"Algorithm: {algo_name}")
        print("="*50)
        
        fold_results = []
        
        for fold_idx in range(5):
            print(f"Fold {fold_idx + 1}/5:")
            
            # Load data
            trainset, test_set = load_fold_data(fold_idx)
            print(f"  Train: {trainset.n_ratings} ratings, Test: {len(test_set)} ratings")
            
            # Run
            metrics = run_algorithm(algo_class, trainset, test_set, algo_name, fold_idx)
            print(f"  RMSE: {metrics['RMSE']:.4f}, MAE: {metrics['MAE']:.4f}")
            
            fold_results.append(metrics)
            
            # Store per-fold
            if algo_name not in results["per_fold"]:
                results["per_fold"][algo_name] = {}
            results["per_fold"][algo_name][f"fold_{fold_idx + 1}"] = metrics
        
        # Tính mean & std
        mean_rmse = sum(f["RMSE"] for f in fold_results) / 5
        std_rmse = (sum((f["RMSE"] - mean_rmse) ** 2 for f in fold_results) / 5) ** 0.5
        mean_mae = sum(f["MAE"] for f in fold_results) / 5
        std_mae = (sum((f["MAE"] - mean_mae) ** 2 for f in fold_results) / 5) ** 0.5
        
        results["summary"][algo_name] = {
            "RMSE": {"mean": round(mean_rmse, 4), "std": round(std_rmse, 4)},
            "MAE": {"mean": round(mean_mae, 4), "std": round(std_mae, 4)},
            "Fit Time": {"mean": round(sum(f["Fit Time"] for f in fold_results) / 5, 2)},
            "Test Time": {"mean": round(sum(f["Test Time"] for f in fold_results) / 5, 2)},
        }
    
    return results


def save_reports(results):
    """Lưu kết quả ra JSON và CSV."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON
    json_path = OUTPUT_DIR / f"cv_results_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ JSON saved: {json_path}")
    
    # CSV summary
    csv_path = OUTPUT_DIR / f"cv_summary_{timestamp}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Algorithm", "RMSE Mean", "RMSE Std", "MAE Mean", "MAE Std", "Fit Time (s)", "Test Time (s)"])
        
        for algo, metrics in results["summary"].items():
            writer.writerow([
                algo,
                metrics["RMSE"]["mean"],
                metrics["RMSE"]["std"],
                metrics["MAE"]["mean"],
                metrics["MAE"]["std"],
                metrics["Fit Time"]["mean"],
                metrics["Test Time"]["mean"],
            ])
    print(f"✅ CSV saved: {csv_path}")
    
    # In bảng tóm tắt
    print("\n" + "="*70)
    print("CROSS-VALIDATION SUMMARY")
    print("="*70)
    print(f"{'Algorithm':<15} {'RMSE':>10} {'MAE':>10} {'Fit(s)':>10} {'Test(s)':>10}")
    print("-"*70)
    for algo, metrics in sorted(results["summary"].items(), key=lambda x: x[1]["RMSE"]["mean"]):
        print(f"{algo:<15} {metrics['RMSE']['mean']:.4f}±{metrics['RMSE']['std']:.4f} "
              f"{metrics['MAE']['mean']:.4f}±{metrics['MAE']['std']:.4f} "
              f"{metrics['Fit Time']['mean']:>8.2f} {metrics['Test Time']['mean']:>9.2f}")
    print("="*70)
    
    return json_path, csv_path


if __name__ == "__main__":
    print("="*60)
    print("5-FOLD CROSS-VALIDATION - MovieLens Dataset")
    print("="*60)
    
    results = run_cv()
    save_reports(results)
    
    print("\n🎉 Hoàn tất!")
