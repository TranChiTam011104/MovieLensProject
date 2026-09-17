# Deploy lên Google Cloud Run

## Prerequisites

### 1. Cài đặt Google Cloud SDK

```bash
# Windows (dùng PowerShell)
curl https://sdk.cloud.google.com | bash

# Hoặc download trực tiếp
# https://cloud.google.com/sdk/docs/install-sdk
```

### 2. Khởi tạo gcloud

```bash
gcloud init
gcloud auth login
```

## Các bước deploy

### Cách 1: Dùng script (Linux/Mac/WSL)

```bash
# Set project ID
export GCP_PROJECT_ID="your-project-id"

# Chạy script
chmod +x deploy-gcloud.sh
./deploy-gcloud.sh
```

### Cách 2: Deploy thủ công

```bash
# 1. Set variables
export PROJECT_ID="your-gcp-project-id"
export REGION="asia-southeast1"

# 2. Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com

# 3. Build image
gcloud builds submit --tag gcr.io/${PROJECT_ID}/movielens-api

# 4. Deploy
gcloud run deploy movielens-api \
    --image gcr.io/${PROJECT_ID}/movielens-api \
    --platform managed \
    --region ${REGION} \
    --port 8000 \
    --memory 512Mi \
    --cpu 1 \
    --allow-unauthenticated
```

## Sau khi deploy

```
🌐 Service URL: https://movielens-api-xxxx-ase.run.app
📖 API Docs:    https://movielens-api-xxxx-ase.run.app/docs
❤️  Health:     https://movielens-api-xxxx-ase.run.app/health
```

## Xem logs

```bash
gcloud run services logs read movielens-api --region asia-southeast1
```

## Update deployment

```bash
# Build lại image
gcloud builds submit --tag gcr.io/${PROJECT_ID}/movielens-api

# Deploy lại
gcloud run deploy movielens-api \
    --image gcr.io/${PROJECT_ID}/movielens-api \
    --platform managed \
    --region asia-southeast1
```

## Tổng chi phí ước tính (Google Cloud Run)

| Resource | Specification | Cost |
|----------|---------------|------|
| CPU | 1 vCPU | ~$0.00002400/vCPU-second |
| Memory | 512 MB | ~$0.00000500/GiB-second |
| Requests | First 2M/month free | $0.40/million |
| Build time | ~2-3 min/build | ~$0.01/build |

**Ước tính**: ~$5-20/tháng cho moderate usage (100K requests/day)

## Xóa service

```bash
gcloud run services delete movielens-api --region asia-southeast1
```
