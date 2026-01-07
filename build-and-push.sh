#!/bin/bash
# Before Running this script , we have to login docker credentails 
set -e

# ================= CONFIG =================
DOCKERHUB_USERNAME="uday27"
LATEST_TAG_FILE="LATEST_IMAGE_TAG.log"
# Readable tag (date-based)
VERSION_TAG=$(date +"%Y.%m.%d")

# Compose files
COMPOSE_FILES="-f docker-compose.yml -f docker-compose-frontend.yml -f docker-compose-db.yml -f docker-compose-services.yml -f docker-compose-dev.yml"

# Images defined in dev.yml
IMAGES=(
  auth-microservice
  inventory-microservice
  order-microservice
  payment-microservice
  frontend-microservice
)
# =========================================

echo "🚀 Building images using docker-compose (docker-compose.yml + dev.yml)"
docker-compose $COMPOSE_FILES build

echo "🏷️ Tagging & pushing images with tag: $VERSION_TAG"
# Clear file at the beginning of each run
> "$LATEST_TAG_FILE"

for IMAGE in "${IMAGES[@]}"; do
  LOCAL_IMAGE="${IMAGE}:latest"
  REMOTE_IMAGE="${DOCKERHUB_USERNAME}/${IMAGE}:${VERSION_TAG}"

  echo "➡️ Tagging $LOCAL_IMAGE → $REMOTE_IMAGE"
  docker tag "$LOCAL_IMAGE" "$REMOTE_IMAGE"

  echo "⬆️ Pushing $REMOTE_IMAGE"
  docker push "$REMOTE_IMAGE"

  echo "$REMOTE_IMAGE" >> "$LATEST_TAG_FILE"
done

echo "✅ All images built and pushed successfully!"
echo "👉 Use this tag in Kubernetes manifests: $VERSION_TAG"
