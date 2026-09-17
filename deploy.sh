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
    gcloud run revisions list \
        --service ${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --format "value(metadata.name)" \
        2>/dev/null | grep -v "can-" | head -1
}

get_latest_canary_revision() {
    gcloud run revisions list \
        --service ${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --format "value(metadata.name)" \
        2>/dev/null | grep "can-" | head -1
}

show_traffic_status() {
    echo "📊 Current Traffic Distribution:"
    echo ""
    gcloud run services describe ${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --format "table(status.traffic.percent,status.traffic.revisionName,status.traffic.tag)" 2>/dev/null
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
    SUFFIX="prod-$(date +%s)"

    echo "🔑 Configuring Docker authentication for GCR..."
    gcloud auth configure-docker --quiet

    echo "📦 Building Docker image on CI runner..."
    docker build -t ${IMAGE_NAME}:${SUFFIX} .

    echo "📤 Pushing Docker image to Registry..."
    docker push ${IMAGE_NAME}:${SUFFIX}

    echo ""
    echo "🚀 Deploying to Cloud Run (100% Traffic)..."
    gcloud run deploy ${SERVICE_NAME} \
        --image ${IMAGE_NAME}:${SUFFIX} \
        --platform managed \
        --region ${REGION} \
        --port 8000 \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10 \
        --allow-unauthenticated \
        --revision-suffix="${SUFFIX}" \
        --set-env-vars "PYTHONUNBUFFERED=1,LOG_LEVEL=INFO,MODEL_NAME=svd_model_full"

    echo ""
    echo "✅ Production deployed successfully!"
}

deploy_canary() {
    show_header
    echo "🚀 Deploying CANARY (v2.0)..."
    echo "Model: svd_model_fold5"
    echo ""

    gcloud config set project ${PROJECT_ID}
    SUFFIX="can-$(date +%s)"

    echo "🔑 Configuring Docker authentication for GCR..."
    gcloud auth configure-docker --quiet

    echo "📦 Building Docker image on CI runner..."
    docker build -t ${IMAGE_NAME}:${SUFFIX} .

    echo "📤 Pushing Docker image to Registry..."
    docker push ${IMAGE_NAME}:${SUFFIX}

    echo ""
    echo "🚀 Deploying canary revision (No traffic yet)..."
    gcloud run deploy ${SERVICE_NAME} \
        --image ${IMAGE_NAME}:${SUFFIX} \
        --platform managed \
        --region ${REGION} \
        --port 8000 \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 5 \
        --allow-unauthenticated \
        --revision-suffix="${SUFFIX}" \
        --tag canary \
        --no-traffic \
        --set-env-vars "PYTHONUNBUFFERED=1,LOG_LEVEL=INFO,MODEL_NAME=svd_model_fold5"

    echo ""
    echo "✅ Canary deployed successfully! (Current Revision: ${SERVICE_NAME}-${SUFFIX})"
    echo "🔗 Test Canary private URL: https://canary---movielens-api-366360236110.us-central1.run.app"
}

# ============================================================
# TRAFFIC MANAGEMENT COMMANDS
# ============================================================

split_traffic() {
    local CANARY_PERCENT=${1:-10}
    PROD_REV=$(get_prod_revision)
    CANARY_REV=$(get_latest_canary_revision)

    if [ -z "$PROD_REV" ]; then
        echo "❌ No production revision found!"
        exit 1
    fi

    if [ -z "$CANARY_REV" ]; then
        echo "❌ No canary revision found! Run ./deploy.sh canary first."
        exit 1
    fi

    local PROD_PERCENT=$((100 - CANARY_PERCENT))

    echo "🔀 Setting traffic split: ${PROD_PERCENT}% prod / ${CANARY_PERCENT}% canary"
    echo "   Production: ${PROD_REV}"
    echo "   Canary:     ${CANARY_REV}"
    echo ""

    gcloud run services update-traffic ${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --to-revisions "${PROD_REV}=${PROD_PERCENT},${CANARY_REV}=${CANARY_PERCENT}"

    echo ""
    show_traffic_status
}

promote_canary() {
    CANARY_REV=$(get_latest_canary_revision)

    if [ -z "$CANARY_REV" ]; then
        echo "❌ No canary revision found to promote!"
        exit 1
    fi

    echo "🚀 Promoting CANARY (${CANARY_REV}) to 100% traffic..."
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
        echo "❌ No production revision found to rollback!"
        exit 1
    fi

    echo "🔙 Rolling back to 100% production..."
    echo "   Target Revision: ${PROD_REV}"
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

show_help() {
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  production          Deploy v1.0 and allocate 100% traffic"
    echo "  canary              Deploy v2.0 as canary (0% traffic, has private tag)"
    echo "  split [percent]     Split traffic (e.g. 10 -> 90% prod / 10% canary)"
    echo "  promote             Give 100% traffic to current canary revision"
    echo "  rollback            Revert 100% traffic back to latest production revision"
    echo "  status              View current traffic split"
    echo "  logs [revision]     View execution logs"
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
        show_help
        exit 1
        ;;
esac