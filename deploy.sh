#!/bin/bash
# ============================================================
# MovieLens API - Unified Deployment & Canary Management Script
# ============================================================
# Usage:
#   ./deploy.sh production          # Deploy v1.0 (svd_model_full)
#   ./deploy.sh canary              # Deploy v2.0 (svd_model_fold5)
#   ./deploy.sh split [percent]     # Set traffic split (default 10%)
#   ./deploy.sh promote             # Promote canary to 100%
#   ./deploy.sh rollback            # Rollback to 100% production
#   ./deploy.sh status              # Show current traffic split
#   ./deploy.sh logs [revision]     # Show logs (optional: specific revision)
# ============================================================

set -e

# ============================================================
# CONFIGURATION
# ============================================================
PROJECT_ID=${GCP_PROJECT_ID:-"vsfintern"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="movielens-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Revision tracking (auto-detected via 'status' command)
PROD_REV=""
CANARY_REV="movielens-api--canary"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

show_header() {
    echo "=============================================="
    echo "🎬 MovieLens API - Deployment Manager"
    echo "=============================================="
    echo "Project: ${PROJECT_ID}"
    echo "Region:  ${REGION}"
    echo "Service: ${SERVICE_NAME}"
    echo "=============================================="
}

get_prod_revision() {
    # Get latest non-canary revision (production)
    gcloud run revisions list \
        --service ${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --format "value(metadata.name)" \
        2>/dev/null | grep -v canary | head -1
}

show_traffic_status() {
    echo "📊 Current Traffic Distribution:"
    echo ""
    gcloud run services describe ${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --format "table(status.traffic.percent,status.traffic.revisionName)" 2>/dev/null
    echo ""
    echo "Service URL: https://movielens-api-366360236110.us-central1.run.app"
}

# ============================================================
# DEPLOYMENT COMMANDS
# ============================================================

deploy_production() {
    show_header
    echo "🚀 Deploying PRODUCTION (v1.0)..."
    echo "Model: svd_model_full"
    echo ""

    gcloud config set project ${PROJECT_ID}

    echo "📦 Building Docker image..."
    gcloud builds submit --no-stream \
        --tag ${IMAGE_NAME} \
        --timeout 10m

    echo ""
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

    echo ""
    echo "✅ Production deployed successfully!"
}

deploy_canary() {
    show_header
    echo "🚀 Deploying CANARY (v2.0)..."
    echo "Model: svd_model_fold5"
    echo ""

    gcloud config set project ${PROJECT_ID}

    echo "📦 Building Docker image..."
    gcloud builds submit --no-stream \
        --tag ${IMAGE_NAME}:canary \
        --timeout 10m

    echo ""
    echo "🚀 Deploying canary revision..."
    gcloud run deploy ${SERVICE_NAME} \
        --image ${IMAGE_NAME}:canary \
        --platform managed \
        --region ${REGION} \
        --port 8000 \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 5 \
        --allow-unauthenticated \
        --revision-suffix="-canary" \
        --set-env-vars "MODEL_NAME=svd_model_fold5" \
        --set-env-vars "PYTHONUNBUFFERED=1" \
        --set-env-vars "LOG_LEVEL=INFO"

    echo ""
    echo "✅ Canary deployed successfully!"
}

# ============================================================
# TRAFFIC MANAGEMENT COMMANDS
# ============================================================

split_traffic() {
    local CANARY_PERCENT=${1:-10}
    PROD_REV=$(get_prod_revision)

    if [ -z "$PROD_REV" ]; then
        echo "❌ No production revision found!"
        echo "   Run: ./deploy.sh production first"
        exit 1
    fi

    echo "🔀 Setting traffic split: $((100 - CANARY_PERCENT))% prod / ${CANARY_PERCENT}% canary"
    echo "   Production: ${PROD_REV}"
    echo "   Canary:     ${CANARY_REV}"
    echo ""

    gcloud run services update-traffic ${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --to-revisions "${PROD_REV}=$((100 - CANARY_PERCENT)),${CANARY_REV}=${CANARY_PERCENT}"

    echo ""
    show_traffic_status
}

promote_canary() {
    echo "🚀 Promoting CANARY to 100% traffic..."
    echo ""

    gcloud run services update-traffic ${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --to-revisions "${CANARY_REV}=100"

    echo ""
    echo "✅ Canary promoted to production!"
    show_traffic_status
}

rollback_canary() {
    PROD_REV=$(get_prod_revision)

    if [ -z "$PROD_REV" ]; then
        echo "❌ No production revision found!"
        exit 1
    fi

    echo "🔙 Rolling back to 100% production..."
    echo "   Revision: ${PROD_REV}"
    echo ""

    gcloud run services update-traffic ${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --to-revisions "${PROD_REV}=100"

    echo ""
    echo "✅ Rolled back to production!"
    show_traffic_status
}

# ============================================================
# MONITORING COMMANDS
# ============================================================

show_logs() {
    local REVISION=${1:-""}

    if [ -n "$REVISION" ]; then
        echo "📋 Logs for revision: ${REVISION}"
        gcloud run services logs read ${SERVICE_NAME} \
            --platform managed \
            --region ${REGION} \
            --limit 30 \
            --format "text(textPayload)" 2>/dev/null | tail -30
    else
        echo "📋 Recent logs (all revisions):"
        gcloud run services logs read ${SERVICE_NAME} \
            --platform managed \
            --region ${REGION} \
            --limit 30 \
            --format "text(textPayload)" 2>/dev/null
    fi
}

# ============================================================
# MAIN DISPATCHER
# ============================================================

show_help() {
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Deployment Commands:"
    echo "  production              Deploy v1.0 to production"
    echo "  canary                  Deploy v2.0 as canary revision"
    echo ""
    echo "Traffic Management:"
    echo "  split [percent]         Set canary traffic % (default: 10)"
    echo "  promote                 Promote canary to 100% traffic"
    echo "  rollback                Rollback to 100% production"
    echo ""
    echo "Monitoring:"
    echo "  status                  Show current traffic distribution"
    echo "  logs [revision]         Show recent logs (optional: specific revision)"
    echo ""
    echo "Examples:"
    echo "  $0 production           # Deploy v1.0"
    echo "  $0 canary               # Deploy v2.0 as canary"
    echo "  $0 split 10             # 90% prod, 10% canary"
    echo "  $0 split 25             # 75% prod, 25% canary"
    echo "  $0 promote              # Promote canary to 100%"
    echo "  $0 rollback             # Rollback to production"
    echo "  $0 status               # View traffic split"
    echo "  $0 logs movielens-api--canary  # Logs for canary revision"
}

case "$1" in
    production|prod)
        deploy_production
        ;;
    canary)
        deploy_canary
        ;;
    split)
        split_traffic "$2"
        ;;
    promote)
        promote_canary
        ;;
    rollback)
        rollback_canary
        ;;
    status)
        show_traffic_status
        ;;
    logs)
        show_logs "$2"
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
