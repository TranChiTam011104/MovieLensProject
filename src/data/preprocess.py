"""
Preprocessing Module - Chuyển đổi data sang format surprise.

TẠI SAO CẦN PREPROCESS:
- Surprise library yêu cầu format cố định
- Data gốc cần được validate và clean
- Tách train/test set để đánh giá model

SURPRISE FORMAT:
- Input: DataFrame với columns: user, item, rating (tên có thể khác)
- Output: Surprise Dataset object sẵn sàng cho training
"""

import pandas as pd
from surprise import Dataset, Reader
from surprise.model_selection import train_test_split

# Import từ config
from ..utils.config import N_CV_FOLDS


def prepare_data_for_surprise(
    df: pd.DataFrame,
    rating_scale: tuple = (1, 5),
    user_col: str = "user_id",
    item_col: str = "item_id",
    rating_col: str = "rating"
) -> Dataset:
    """
    Chuyển đổi DataFrame sang Surprise Dataset.
    
    ARGS:
        df: DataFrame chứa ratings
        rating_scale: Scale của ratings (default 1-5)
        user_col: Tên column user_id
        item_col: Tên column item_id  
        rating_col: Tên column rating
    
    RETURNS:
        Surprise Dataset object
    
    VÍ DỤ:
        >>> from src.data import load_ratings
        >>> df = load_ratings()
        >>> dataset = prepare_data_for_surprise(df)
    """
    # TODO: Implement
    # Gợi ý:
    # 1. Tạo Reader object với rating_scale
    # 2. Tạo Dataset.load_from_df() với df[[user_col, item_col, rating_col]]
    # 3. Return Dataset object
    reader = Reader(rating_scale=rating_scale)
    dataset = Dataset.load_from_df(df[[user_col, item_col, rating_col]], reader)
    return dataset


def get_train_test_split(
    dataset: Dataset,
    test_size: float = 0.2,
    random_state: int = 42
) -> tuple:
    """
    Tách dataset thành train và test set.
    
    ARGS:
        dataset: Surprise Dataset
        test_size: Tỷ lệ test (0.2 = 20%)
        random_state: Seed cho reproducibility
    
    RETURNS:
        Tuple (trainset, testset)
    
    VÍ DỤ:
        >>> trainset, testset = get_train_test_split(dataset)
        >>> print(f"Train: {len(trainset.all_users())} users")
        >>> print(f"Test: {len(testset)} ratings")
    """
    # TODO: Implement
    # Gợi ý:
    # 1. Gọi Dataset.build_trainset_testset() 
    #    HOẶC dùng model_selection.train_test_split()
    # 2. Return (trainset, testset)
    return train_test_split(dataset, test_size=test_size, random_state=random_state)


def get_crossvalidation_folds(
    dataset: Dataset,
    n_folds: int = 5,
    random_state: int = 42
):
    """
    Tạo n folds cho cross-validation.
    
    ARGS:
        dataset: Surprise Dataset
        n_folds: Số folds (thường 5)
        random_state: Seed cho reproducibility
    
    RETURNS:
        Iterable của (trainset, testset) tuples
    
    VÍ DỤ:
        >>> for trainset, testset in get_crossvalidation_folds(dataset, n_folds=5):
        ...     # Train và evaluate model
        ...     pass
    """
    # TODO: Implement
    # Gợi ý:
    # 1. Import KFold từ surprise.model_selection
    # 2. Tạo KFold object với n_folds và random_state
    # 3. Return kf.split(dataset)
    pass


def load_splits_from_files(
    base_file: str,
    test_file: str,
    data_dir: str
) -> tuple:
    """
    Load train/test splits từ file đã có (u1.base/u1.test).
    
    MovieLens đã cung cấp sẵn các splits, dùng cái này thay vì tự tách.
    
    ARGS:
        base_file: Tên file training (vd: "u1.base")
        test_file: Tên file test (vd: "u1.test")
        data_dir: Thư mục chứa files
    
    RETURNS:
        Tuple (trainset, testset)
    
    VÍ DỤ:
        >>> trainset, testset = load_splits_from_files(
        ...     base_file="u1.base",
        ...     test_file="u1.test",
        ...     data_dir="data/raw"
        ... )
    """
    # TODO: Implement
    # Gợi ý:
    # 1. Load base_file vào DataFrame (tab-separated)
    # 2. Load test_file vào DataFrame
    # 3. Convert sang surprise format
    # 4. Build trainset từ base_df
    # 5. Return (trainset, testset)
    pass


def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate data trước khi train.
    
    CHECKS:
    - Không có missing values
    - Ratings trong range hợp lệ (1-5)
    - User/Item IDs hợp lệ
    
    RETURNS:
        True nếu data hợp lệ, raises ValueError nếu không
    
    VÍ DỤ:
        >>> df = load_ratings()
        >>> validate_data(df)
        True  # hoặc raise ValueError("Missing values found")
    """
    # TODO: Implement
    # Gợi ý:
    # 1. Check for missing values
    # 2. Check rating range (1-5)
    # 3. Check for negative user/item IDs
    # 4. Return True hoặc raise ValueError
    pass


def process_movies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process movie data - extract genres and release year.
    
    ARGS:
        df: DataFrame with movie data from u.item
        
    RETURNS:
        DataFrame with columns: movie_id, title, genres, release_year, avg_rating, n_ratings
    
    VÍ DỤ:
        >>> movies_df = load_movies()
        >>> processed = process_movies(movies_df)
        >>> print(processed.head())
    """
    import re
    
    # Copy to avoid modifying original
    df = df.copy()
    
    # Basic columns
    result = pd.DataFrame()
    result['movie_id'] = df['movie_id']
    result['title'] = df['title']
    
    # Extract release year from title (format: "Title, The (1994)")
    def extract_year(title):
        match = re.search(r'\((\d{4})\)$', str(title))
        return int(match.group(1)) if match else None
    
    result['release_year'] = df['title'].apply(extract_year)
    
    # Extract genres from genre columns (genre_0 to genre_18)
    genre_cols = [col for col in df.columns if col.startswith('genre_')]
    
    # Genre names (in order from MovieLens documentation)
    GENRE_NAMES = [
        'unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy',
        'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
        'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
    ]
    
    # Create genres list for each movie
    def get_genres(row):
        genres = []
        for i, col in enumerate(sorted(genre_cols)):
            if row[col] == 1 and i < len(GENRE_NAMES):
                genres.append(GENRE_NAMES[i])
        return genres
    
    result['genres'] = df.apply(get_genres, axis=1)
    
    # Placeholder for ratings info (will be computed from ratings data)
    result['avg_rating'] = None
    result['n_ratings'] = 0
    
    return result


def add_rating_stats(
    movies_df: pd.DataFrame,
    ratings_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Add rating statistics to movies DataFrame.
    
    Computes avg_rating and n_ratings from ratings data.
    
    ARGS:
        movies_df: Processed movies DataFrame
        ratings_df: Ratings DataFrame
        
    RETURNS:
        movies_df with avg_rating and n_ratings columns filled
    """
    # Compute stats from ratings
    rating_stats = ratings_df.groupby('item_id').agg(
        n_ratings=('rating', 'count'),
        avg_rating=('rating', 'mean')
    ).reset_index()

    # Merge with movies
    result = movies_df.copy()
    result = result.merge(
        rating_stats,
        left_on='movie_id',
        right_on='item_id',
        how='left'
    )

    # Ensure columns exist (handle edge case where merge produces nothing)
    if 'avg_rating' not in result.columns:
        result['avg_rating'] = 0.0
    else:
        result['avg_rating'] = result['avg_rating'].fillna(0)
    
    if 'n_ratings' not in result.columns:
        result['n_ratings'] = 0
    else:
        result['n_ratings'] = result['n_ratings'].fillna(0).astype(int)
    
    # Drop redundant item_id column if exists
    if 'item_id' in result.columns:
        result.drop('item_id', axis=1, inplace=True)
    
    return result


# ============================================================
# MAIN - Test nếu chạy trực tiếp
# ============================================================

if __name__ == "__main__":
    print("Testing preprocessing...")
    
    # Import data loading functions
    from .load import load_ratings
    
    try:
        # Load data
        df = load_ratings()
        print(f"✅ Loaded {len(df)} ratings")
        
        # Validate
        try:
            validate_data(df)
            print("✅ Data validation passed")
        except ValueError as e:
            print(f"❌ Validation failed: {e}")
        
        # Convert to surprise
        try:
            dataset = prepare_data_for_surprise(df)
            print("✅ Converted to Surprise format")
        except NotImplementedError:
            print("❌ prepare_data_for_surprise() chưa implement")
            
    except NotImplementedError:
        print("❌ load_ratings() chưa implement - cần implement load.py trước")
    except Exception as e:
        print(f"❌ Error: {e}")
