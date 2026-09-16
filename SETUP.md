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
├── src/             # Source code
│   ├── api/         # FastAPI app (routers, services)
│   ├── data/        # Data loading & preprocessing
│   ├── models/      # Model training
│   └── utils/       # Configuration
├── models/           # Trained model artifacts
├── data/             # Raw & processed data
├── scripts/          # Training & evaluation scripts
├── tests/            # Unit & integration tests
├── configs/          # YAML configuration files
├── postman-collections/  # API testing collections
├── reports/          # CV results & experiments
├── docs/             # Documentation
│   └── api/          # API spec & use cases
├── .github/workflows/ # CI/CD pipelines
├── deploy.sh          # Manual deployment script
├── Dockerfile
└── docker-compose.yml
```

## 6. Chạy Local Development

### Start API
```bash
uvicorn src.api.main:app --reload --port 8000
```

### Run Tests
```bash
pytest tests/ -v
```

## 7. Docker
```bash
docker-compose up --build
```

## 8. Setup Pre-commit (Optional)
```bash
pre-commit install
```
