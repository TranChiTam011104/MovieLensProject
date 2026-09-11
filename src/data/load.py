"""
Data Loading Module - Load data từ raw folder.

CHỨC NĂNG:
- load_ratings(): Đọc file u.data (100K ratings)
- load_movies(): Đọc file u.item (thông tin phim)
- load_users(): Đọc file u.user (thông tin user)

TẠI SAO TÁCH RIÊNG:
- Tái sử dụng ở nhiều nơi (EDA, train, test)
- Thay đổi data source chỉ cần sửa 1 file
- Dễ mock data cho testing
"""

import pandas as pd
from pathlib import Path

# Import config
from ..utils.config import (
    RAW_DATA_DIR,
    RATINGS_FILE,
    MOVIES_FILE,
    USERS_FILE,
    GENRES_FILE,
    RATINGS_COLUMNS,
    MOVIES_COLUMNS,
)


def load_ratings(filepath: Path = None) -> pd.DataFrame:
    """
    Load ratings data từ u.data file.
    
    DATA FORMAT (tab-separated):
    user_id | item_id | rating | timestamp
    
    RETURNS:
        pd.DataFrame với columns: user_id, item_id, rating, timestamp
    
    VÍ DỤ:
        >>> df = load_ratings()
        >>> print(df.head())
           user_id  item_id  rating  timestamp
        0      196      242       3  881250949
        1      186      302       3  891717742
        2       22      377       1  878887116
    """
    # TODO: Implement
    # Gợi ý:
    # 1. Nếu filepath = None, dùng RATINGS_FILE trong RAW_DATA_DIR
    # 2. Dùng pd.read_csv() với separator='\t'
    # 3. Gán header=None, names=RATINGS_COLUMNS
    
    if filepath is None:
        filepath = RAW_DATA_DIR / RATINGS_FILE
    df = pd.read_csv(filepath, sep='\t', header=None, names=RATINGS_COLUMNS)
    
    return df
    


def load_users(filepath: Path = None) -> pd.DataFrame:
    """
    Load users demographic data từ u.user file.
    
    DATA FORMAT (tab-separated):
    user_id | age | gender | occupation | zip code
    
    RETURNS:
        pd.DataFrame với thông tin user
    
    VÍ DỤ:
        >>> df = load_users()
        >>> print(df.head())
           user_id  age gender  occupation  zip_code
        0        1   24      M  technician    85711
    """
    # TODO: Implement
    # Gợi ý:
    # 1. Nếu filepath = None, dùng USERS_FILE trong RAW_DATA_DIR
    # 2. Dùng pd.read_csv() với separator='|'
    # 3. Gán header=None
    pass


def load_genres(filepath: Path = None) -> pd.DataFrame:
    """
    Load genres list từ u.genre file.
    
    RETURNS:
        pd.DataFrame với 2 columns: genre_id, genre_name
    """
    # TODO: Implement
    # Gợi ý:
    # 1. Đọc file với separator='|'
    # 2. Genre format: "genre_name" (mỗi dòng 1 genre)
    pass


def get_dataset_info() -> dict:
    """
    Trả về thông tin tổng quan về dataset.
    
    RETURNS:
        dict với keys: n_users, n_items, n_ratings
    
    VÍ DỤ:
        >>> info = get_dataset_info()
        >>> print(info)
        {'n_users': 943, 'n_items': 1682, 'n_ratings': 100000}
    """
    # TODO: Implement
    # Gợi ý:
    # 1. Load ratings
    # 2. Đếm unique users, items, total ratings
    pass


# ============================================================
# MAIN - Test nếu chạy trực tiếp
# ============================================================

if __name__ == "__main__":
    print("Testing data loading...")
    
    # Test load ratings
    try:
        ratings = load_ratings()
        print(f"✅ Ratings loaded: {len(ratings)} rows")
        print(ratings.head())
        print(f"   Unique users: {ratings['user_id'].nunique()}")
        print(f"   Unique items: {ratings['item_id'].nunique()}")
    except NotImplementedError:
        print("❌ load_ratings() chưa implement")
    except Exception as e:
        print(f"❌ Error: {e}")
