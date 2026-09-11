"""
Configuration module - Lưu trữ constants và paths cho project.

TẠI SAO CẦN FILE NÀY?
- Tránh hardcode paths trong code
- Khi deploy lên server, chỉ cần đổi BASE_DIR
- Tái sử dụng constants ở nhiều nơi
"""

from pathlib import Path

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
# MODEL CONFIG - Cấu hình model
# ============================================================

# Số folds cho cross-validation
N_CV_FOLDS = 5

# Các thuật toán sẽ test
ALGORITHMS = ["SVD", "KNNBasic", "KNNWithMeans", "BaselineOnly"]

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
