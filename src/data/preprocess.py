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
