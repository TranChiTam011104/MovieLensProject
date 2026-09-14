"""
Configuration module - Lưu trữ constants và paths cho project.

TẠI SAO CẦN FILE NÀY?
- Tránh hardcode paths trong code
- Khi deploy lên server, chỉ cần đổi BASE_DIR
- Tái sử dụng constants ở nhiều nơi
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ============================================================
# PATHS - Đường dẫn đến các thư mục
# ============================================================

# Thư mục gốc của project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Thư mục chứa data gốc (từ MovieLens download)
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

# Thư mục chứa data đã xử lý
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Thư mục chứa model đã train
MODELS_DIR = BASE_DIR / "models"

# ============================================================
# FILENAMES - Tên các file data
# ============================================================

# Tên file ratings (100K ratings)
RATINGS_FILE = "u.data"

# Tên file thông tin movies
MOVIES_FILE = "u.item"

# Tên file thông tin users
USERS_FILE = "u.user"

# Tên file genres
GENRES_FILE = "u.genre"

# ============================================================
# TRAIN/TEST SPLIT FILES - Đã có sẵn từ MovieLens
# ============================================================

# 5-fold cross validation (u1-u5)
TRAIN_FILES = ["u1.base", "u2.base", "u3.base", "u4.base", "u5.base"]
TEST_FILES = ["u1.test", "u2.test", "u3.test", "u4.test", "u5.test"]

# Single train/test split (10 ratings/user trong test)
SINGLE_TRAIN_FILE = "ua.base"
SINGLE_TEST_FILE = "ua.test"

# ============================================================
# MODEL CONFIG - Cấu hình model (từ .env)
# ============================================================

# Số folds cho cross-validation
N_CV_FOLDS = 5

# Các thuật toán sẽ test
ALGORITHMS = ["SVD", "KNNBasic", "KNNWithMeans", "BaselineOnly"]

# Model hyperparameters
N_FACTORS = int(os.getenv("N_FACTORS", "100"))
N_EPOCHS = int(os.getenv("N_EPOCHS", "20"))
LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.005"))
REG_ALL = float(os.getenv("REG_ALL", "0.02"))

# ============================================================
# TRAIN/TEST SPLIT CONFIG (từ .env)
# ============================================================

# Fold 1-5 cho 5-fold CV, 0 cho ua.base/ua.test
TRAIN_TEST_FOLD = int(os.getenv("TRAIN_TEST_FOLD", "1"))

# Model output name
MODEL_NAME = os.getenv("MODEL_NAME", "svd_model")

# Dataset stats (cho confidence calculation)
TOTAL_USERS = int(os.getenv("TOTAL_USERS", "943"))
TOTAL_MOVIES = int(os.getenv("TOTAL_MOVIES", "1682"))

# ============================================================
# SIMILARITY SERVICE CONFIG (từ .env)
# ============================================================

SIM_N_FACTORS = int(os.getenv("SIM_N_FACTORS", "100"))
SIM_N_EPOCHS = int(os.getenv("SIM_N_EPOCHS", "20"))
DEFAULT_N_RECOMMENDATIONS = int(os.getenv("DEFAULT_N_RECOMMENDATIONS", "10"))

# ============================================================
# COLUMNS - Tên cột trong data
# ============================================================

# Columns cho ratings data (tab-separated)
RATINGS_COLUMNS = ["user_id", "item_id", "rating", "timestamp"]

# Columns cho movies data
MOVIES_COLUMNS = [
    "movie_id", "title", "release_date", "video_release_date", "IMDb_URL"
] + [f"genre_{i}" for i in range(19)]  # 19 genre flags

# ============================================================
# MODEL FILENAMES - Tên file model output
# ============================================================

MODEL_FILENAMES = {
    "svd": "svd_model.pkl",
    "knn_basic": "knn_basic_model.pkl",
    "knn_means": "knn_means_model.pkl",
    "baseline": "baseline_model.pkl",
}

# Metrics output file
METRICS_FILE = "metrics.json"
