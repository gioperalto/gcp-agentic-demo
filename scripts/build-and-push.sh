#!/usr/bin/env bash
# Build the backend Docker image and push to Artifact Registry.
# Usage: ./scripts/build-and-push.sh [TAG]
#
# Requires: gcloud auth configured, AR_REPO env var set
# Example:
#   export AR_REPO=us-central1-docker.pkg.dev/my-project/travel-planner-prod
#   ./scripts/build-and-push.sh v1.2.3

set -euo pipefail

TAG="${1:-latest}"
IMAGE_NAME="travel-planner-api"

if [ -z "${AR_REPO:-}" ]; then
  echo "Error: AR_REPO environment variable is not set."
  echo "Example: export AR_REPO=us-central1-docker.pkg.dev/PROJECT/REPO"
  exit 1
fi

echo "Building ${AR_REPO}/${IMAGE_NAME}:${TAG} ..."
docker build -t "${AR_REPO}/${IMAGE_NAME}:${TAG}" -f backend/Dockerfile .

echo "Configuring Docker for Artifact Registry ..."
gcloud auth configure-docker "$(echo "${AR_REPO}" | cut -d/ -f1)" --quiet

echo "Pushing ${AR_REPO}/${IMAGE_NAME}:${TAG} ..."
docker push "${AR_REPO}/${IMAGE_NAME}:${TAG}"

echo "Done. Deploy with:"
echo "  gcloud run deploy SERVICE_NAME --image ${AR_REPO}/${IMAGE_NAME}:${TAG} --region REGION"
