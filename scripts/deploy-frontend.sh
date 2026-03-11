#!/usr/bin/env bash
# Build the frontend and upload dist/ to the GCS bucket.
# Usage: ./scripts/deploy-frontend.sh
#
# Requires: DEPLOY_BUCKET and VITE_API_BASE_URL env vars set
# Example:
#   export DEPLOY_BUCKET=my-project-frontend-prod
#   export VITE_API_BASE_URL=https://travel.example.com
#   ./scripts/deploy-frontend.sh

set -euo pipefail

if [ -z "${DEPLOY_BUCKET:-}" ]; then
  echo "Error: DEPLOY_BUCKET environment variable is not set."
  exit 1
fi

if [ -z "${VITE_API_BASE_URL:-}" ]; then
  echo "Error: VITE_API_BASE_URL environment variable is not set."
  exit 1
fi

echo "Installing frontend dependencies ..."
cd frontend
npm ci

echo "Building frontend (VITE_API_BASE_URL=${VITE_API_BASE_URL}) ..."
npm run build

echo "Syncing dist/ to gs://${DEPLOY_BUCKET} ..."
gsutil -m rsync -r -d dist "gs://${DEPLOY_BUCKET}"

echo "Done. Frontend deployed to gs://${DEPLOY_BUCKET}"
echo "If CDN is enabled, invalidate cache:"
echo "  gcloud compute url-maps invalidate-cdn-cache URL_MAP_NAME --path=/index.html"
