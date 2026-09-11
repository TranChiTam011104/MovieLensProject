# Hướng Dẫn Setup Dự Án

## 1. Clone Repository
```bash
git clone <repo-url>
cd MovieLensProject
```

## 2. Tạo Virtual Environment

### Với venv (Python built-in)
```bash
# Tạo virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### Với conda
```bash
conda create -n movielens python=3.10
conda activate movielens
```

## 3. Cài Đặt Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# Dev dependencies (optional)
pip install -r requirements-dev.txt
```

## 4. Tải Dataset MovieLens 100K
```bash
# Dataset sẽ được lưu ở data/raw/
# Có thể tải từ: https://grouplens.org/datasets/movielens/ml-100k/
```

## 5. Cấu Trúc Thư Mục

```
MovieLensProject/
├── data/           # Dữ liệu (raw & processed)
├── src/             # Source code
│   ├── model/       # Model training
│   ├── api/         # FastAPI app
│   ├── features/    # Feature engineering
│   └── serving/     # Serving logic
├── tests/           # Unit & integration tests
├── configs/         # Configuration files
├── docker/          # Docker files
├── scripts/          # Utility scripts
├── docs/             # Documentation
├── notebooks/        # EDA & experiments
└── .github/          # CI/CD workflows
```

## 6. Chạy Local Development

### Start API
```bash
cd src/api
uvicorn main:app --reload --port 8000
```

### Run Tests
```bash
pytest tests/ -v
```

## 7. Docker
```bash
cd docker
docker-compose up --build
```

## 8. Setup Pre-commit (Optional)
```bash
pre-commit install
```
