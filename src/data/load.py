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
    USERS_COLUMNS,
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
    
    DATA FORMAT (pipe-separated):
    user_id | age | gender | occupation | zip code
    
    RETURNS:
        pd.DataFrame với thông tin user
    
    VÍ DỤ:
        >>> df = load_users()
        >>> print(df.head())
           user_id  age gender  occupation  zip_code
        0        1   24      M  technician    85711
    """
    if filepath is None:
        filepath = RAW_DATA_DIR / USERS_FILE
    
    df = pd.read_csv(filepath, sep='|', header=None, names=USERS_COLUMNS)
    return df


def load_genres(filepath: Path = None) -> pd.DataFrame:
    """
    Load genres list từ u.genre file.
    
    DATA FORMAT (pipe-separated, không có header):
    genre_name|genre_id (mỗi dòng 1 genre)
    
    RETURNS:
        pd.DataFrame với 2 columns: genre_id, genre_name
    
    VÍ DỤ:
        >>> df = load_genres()
        >>> print(df.head())
           genre_id genre_name
        0        0    unknown
        1        1     Action
    """
    if filepath is None:
        filepath = RAW_DATA_DIR / GENRES_FILE
    
    df = pd.read_csv(filepath, sep='|', header=None, names=['genre_name', 'genre_id'])
    # Sắp xếp theo genre_id
    df = df.sort_values('genre_id').reset_index(drop=True)
    return df


def load_train_test_data(fold: int = 1, model_name: str = None) -> tuple:
    """
    Load train và test data từ MovieLens pre-split files.
    
    MovieLens đã có sẵn 5-fold cross validation splits:
    - u1.base/u1.test, u2.base/u2.test, ..., u5.base/u5.test
    - ua.base/ua.test, ub.base/ub.test (10 ratings/user trong test)
    
    Nếu model_name chứa "full", sẽ load u.data thay vì fold split.
    
    ARGS:
        fold: Fold number (1-5) cho cross validation, 
              hoặc 0 cho ua.base/ua.test
        model_name: Tên model (nếu chứa "full" sẽ load u.data)
    
    RETURNS:
        Tuple (train_df, test_df) với columns: user_id, item_id, rating, timestamp
        Với full data: test_df sẽ là None
    
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
        SINGLE_TEST_FILE,
        RATINGS_FILE
    )
    
    # Xác định fold từ model_name nếu được cung cấp
    if model_name is not None:
        from ..utils.config import get_fold_from_model_name
        fold = get_fold_from_model_name(model_name)
    
    if fold == -1:
        # Full data - dùng u.data cho cả train
        train_path = RAW_DATA_DIR / RATINGS_FILE
        train_df = pd.read_csv(train_path, sep='\t', header=None, names=RATINGS_COLUMNS)
        return train_df, None
    elif fold == 0:
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
        dict với keys: n_users, n_items, n_ratings, n_genres
    
    VÍ DỤ:
        >>> info = get_dataset_info()
        >>> print(info)
        {'n_users': 943, 'n_items': 1682, 'n_ratings': 100000, 'n_genres': 18}
    """
    ratings = load_ratings()
    
    info = {
        "n_users": int(ratings['user_id'].nunique()),
        "n_items": int(ratings['item_id'].nunique()),
        "n_ratings": len(ratings),
    }
    
    # Thử load genres nếu có
    try:
        genres = load_genres()
        info["n_genres"] = len(genres)
    except Exception:
        info["n_genres"] = None
    
    return info


def get_movie_genres(movie_row: pd.Series) -> list:
    """
    Lấy danh sách genres từ movie row.
    
    ARGS:
        movie_row: Một dòng từ movies DataFrame
    
    RETURNS:
        List of genre names (ví dụ: ['Action', 'Comedy', 'Drama'])
    """
    from ..utils.config import GENRES_LIST
    
    genres = []
    for i, genre_name in enumerate(GENRES_LIST):
        if movie_row.get(f'genre_{i}', 0) == 1:
            genres.append(genre_name)
    return genres


def get_user_info(user_id: int, users_df: pd.DataFrame = None) -> dict:
    """
    Lấy thông tin user.
    
    ARGS:
        user_id: ID của user
        users_df: DataFrame users (sẽ load nếu None)
    
    RETURNS:
        Dict chứa thông tin user
    """
    if users_df is None:
        users_df = load_users()
    
    user_row = users_df[users_df['user_id'] == user_id]
    if len(user_row) == 0:
        return None
    
    return user_row.iloc[0].to_dict()


def get_movie_info(movie_id: int, movies_df: pd.DataFrame = None) -> dict:
    """
    Lấy thông tin movie.
    
    ARGS:
        movie_id: ID của movie
        movies_df: DataFrame movies (sẽ load nếu None)
    
    RETURNS:
        Dict chứa thông tin movie (bao gồm cả genres)
    """
    if movies_df is None:
        movies_df = load_movies()
    
    movie_row = movies_df[movies_df['movie_id'] == movie_id]
    if len(movie_row) == 0:
        return None
    
    info = movie_row.iloc[0].to_dict()
    info['genres'] = get_movie_genres(movie_row.iloc[0])
    return info


# ============================================================
# MAIN - Test nếu chạy trực tiếp
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing data loading...")
    print("=" * 60)
    
    # Test load ratings
    try:
        ratings = load_ratings()
        print(f"\n✅ Ratings loaded: {len(ratings)} rows")
        print(f"   Columns: {list(ratings.columns)}")
        print(ratings.head(3))
    except Exception as e:
        print(f"❌ Error loading ratings: {e}")
    
    # Test load movies
    try:
        movies = load_movies()
        print(f"\n✅ Movies loaded: {len(movies)} rows")
        print(f"   Columns: {list(movies.columns)}")
        print(movies[['movie_id', 'title']].head(3))
    except Exception as e:
        print(f"❌ Error loading movies: {e}")
    
    # Test load users
    try:
        users = load_users()
        print(f"\n✅ Users loaded: {len(users)} rows")
        print(f"   Columns: {list(users.columns)}")
        print(users.head(3))
    except Exception as e:
        print(f"❌ Error loading users: {e}")
    
    # Test load genres
    try:
        genres = load_genres()
        print(f"\n✅ Genres loaded: {len(genres)} rows")
        print(genres)
    except Exception as e:
        print(f"❌ Error loading genres: {e}")
    
    # Test get_dataset_info
    try:
        info = get_dataset_info()
        print(f"\n✅ Dataset info: {info}")
    except Exception as e:
        print(f"❌ Error getting dataset info: {e}")
    
    # Test helper functions
    try:
        movie_info = get_movie_info(1)
        if movie_info:
            print(f"\n✅ Movie info (ID=1): {movie_info['title']}")
            print(f"   Genres: {movie_info['genres']}")
    except Exception as e:
        print(f"❌ Error getting movie info: {e}")
    
    try:
        user_info = get_user_info(1)
        if user_info:
            print(f"\n✅ User info (ID=1): age={user_info['age']}, gender={user_info['gender']}")
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
