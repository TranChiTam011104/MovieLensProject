#!/bin/bash
# ============================================================
# Deploy MovieLens API to Google Cloud Run
# ============================================================

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-gcp-project-id"}
REGION=${GCP_REGION:-"asia-southeast1"}
SERVICE_NAME="movielens-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "=============================================="
echo "🚀 Deploying MovieLens API to Google Cloud Run"
echo "=============================================="
echo "Project: ${PROJECT_ID}"
echo "Region:  ${REGION}"
echo "=============================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found. Please install gcloud CLI first."
    exit 1
fi

# Set project
echo "📌 Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com

# Build and push container
echo "📦 Building Docker image..."
gcloud builds submit \
    --tag ${IMAGE_NAME} \
    --timeout 10m

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --port 8000 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --allow-unauthenticated \
    --set-env-vars "PYTHONUNBUFFERED=1" \
    --set-env-vars "LOG_LEVEL=INFO"

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)')

echo ""
echo "=============================================="
echo "✅ Deployment complete!"
echo "=============================================="
echo "🌐 Service URL: ${SERVICE_URL}"
echo "📖 API Docs:    ${SERVICE_URL}/docs"
echo "❤️  Health:     ${SERVICE_URL}/health"
echo "=============================================="
