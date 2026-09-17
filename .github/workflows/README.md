# CI/CD Pipeline

GitHub Actions tự động deploy khi push code.

## 🔄 Luồng hoạt động

```
┌─────────────────────────────────────────────────────────────┐
│  git push                                                    │
│      ↓                                                       │
│  GitHub Actions triggered                                    │
│      ↓                                                       │
│  ┌──────────────────┐                                       │
│  │ 🧪 Test & Lint   │ → flake8 + pytest                     │
│  └────────┬─────────┘                                       │
│           ↓                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Branch = main    → Deploy PRODUCTION (100%)          │   │
│  │ Branch = feature → Deploy CANARY (10%)               │   │
│  │ PR to main       → Run tests only (no deploy)         │   │
│  └──────────────────────────────────────────────────────┘   │
│      ↓                                                       │
│  Smoke test /health                                          │
│      ↓                                                       │
│  ✅ Done!                                                    │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Workflows

| File | Trigger | Job |
|------|---------|-----|
| `deploy.yml` | Push to `main` | Deploy Production |
| `deploy.yml` | Push to `feature/*` | Deploy Canary (10%) |
| `deploy.yml` | Pull Request | Test only |
| `deploy.yml` | Manual dispatch | Promote/Rollback/Set traffic |

## 🚀 Setup (1 lần)

### 1. Tạo GCP Service Account

```bash
gcloud iam service-accounts create github-actions \
    --project=vsfintern \
    --display-name="GitHub Actions Deployer"

gcloud projects add-iam-policy-binding vsfintern \
    --member="serviceAccount:github-actions@vsfintern.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding vsfintern \
    --member="serviceAccount:github-actions@vsfintern.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding vsfintern \
    --member="serviceAccount:github-actions@vsfintern.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud iam service-accounts keys create key.json \
    --iam-account=github-actions@vsfintern.iam.gserviceaccount.com
```

### 2. Add Secret to GitHub

- Vào: **Settings → Secrets and variables → Actions**
- Click **New repository secret**
- Name: `GCP_SA_KEY`
- Value: paste nội dung file `key.json`

### 3. Push code

```bash
# Production deploy
git checkout main
git push origin main

# Canary deploy
git checkout -b feature/my-new-model
git push origin feature/my-new-model
```

## 🎛 Manual Operations

Vào **Actions tab** → **MovieLens CI/CD** → **Run workflow**

| Action | Mô tả |
|--------|-------|
| `deploy-canary` | Deploy model mới với traffic 10% |
| `promote-canary` | Đẩy canary lên 100% |
| `rollback-canary` | Quay về 100% production |
| `set-traffic` | Điều chỉnh % canary traffic |

## 📊 Monitoring

- **GitHub Actions**: Tab "Actions" trong repo
- **Cloud Run Logs**: https://console.cloud.google.com/run/detail/us-central1/movielens-api/logs
- **Traffic Split**: https://console.cloud.google.com/run/detail/us-central1/movielens-api/revisions

## 🔧 Troubleshooting

### Build fails
```bash
# Test locally
docker build -t test-image .
docker run -p 8000:8000 test-image
```

### Auth fails
- Check `GCP_SA_KEY` secret đã add đúng chưa
- Verify SA có đủ permissions (run.admin, storage.admin, iam.serviceAccountUser)

### Health check fails
```bash
# Check logs
gcloud run services logs read movielens-api --region=us-central1 --limit=50
```
