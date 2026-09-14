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
    


def load_movies(filepath: Path = None) -> pd.DataFrame:
    """
    Load movies data từ u.item file.
    
    DATA FORMAT (pipe-separated):
    movie_id | title | release_date | video_release_date | IMDb_URL | 19 genre flags
    
    RETURNS:
        pd.DataFrame với columns như MOVIES_COLUMNS định nghĩa
    
    VÍ DỤ:
        >>> df = load_movies()
        >>> print(df.head())
           movie_id  title  release_date  genre_0  genre_1  ...
        0        1  Toy Story (1995)  01-Jan-1995  0  1  ...
    """
    if filepath is None:
        filepath = RAW_DATA_DIR / MOVIES_FILE
    
    # Read with pipe separator, no header
    df = pd.read_csv(filepath, sep='|', header=None, encoding='latin-1')
    
    # Ensure we have the right number of columns
    if len(df.columns) == 24:
        df.columns = MOVIES_COLUMNS
    else:
        # If different format, create columns dynamically
        df.columns = [f'col_{i}' for i in range(len(df.columns))]
    
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


def load_train_test_data(fold: int = 1) -> tuple:
    """
    Load train và test data từ MovieLens pre-split files.
    
    MovieLens đã có sẵn 5-fold cross validation splits:
    - u1.base/u1.test, u2.base/u2.test, ..., u5.base/u5.test
    - ua.base/ua.test, ub.base/ub.test (10 ratings/user trong test)
    
    ARGS:
        fold: Fold number (1-5) cho cross validation, 
              hoặc 0 cho ua.base/ua.test
    
    RETURNS:
        Tuple (train_df, test_df) với columns: user_id, item_id, rating, timestamp
    
    VÍ DỤ:
        >>> train, test = load_train_test_data(fold=1)
        >>> print(f"Train: {len(train)} ratings")
        >>> print(f"Test: {len(test)} ratings")
    """
    from ..utils.config import (
        RAW_DATA_DIR, 
        TRAIN_FILES, 
        TEST_FILES, 
        SINGLE_TRAIN_FILE, 
        SINGLE_TEST_FILE
    )
    
    if fold == 0:
        # Dùng ua.base/ua.test (10 ratings/user)
        train_path = RAW_DATA_DIR / SINGLE_TRAIN_FILE
        test_path = RAW_DATA_DIR / SINGLE_TEST_FILE
    else:
        # Dùng u{fold}.base/u{fold}.test
        idx = fold - 1  # Convert 1-5 -> 0-4
        train_path = RAW_DATA_DIR / TRAIN_FILES[idx]
        test_path = RAW_DATA_DIR / TEST_FILES[idx]
    
    train_df = pd.read_csv(train_path, sep='\t', header=None, names=RATINGS_COLUMNS)
    test_df = pd.read_csv(test_path, sep='\t', header=None, names=RATINGS_COLUMNS)
    
    return train_df, test_df


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
