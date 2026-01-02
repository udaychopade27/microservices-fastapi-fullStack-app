#!/bin/bash

# --- CONFIGURATION ---
REGION="us-east-1"  
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGISTRY_URL="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

# 1. MOVE TO PROJECT ROOT
# This gets the absolute path of the project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)
echo "Project Root is: $PROJECT_ROOT"

# 2. DEFINE SERVICES (Folder Name : Repository Name)
# USE THE EXACT FOLDER NAMES FROM YOUR TREE
declare -A SERVICES=(
    ["auth-service"]="auth-repo"
    ["inventory-microservice"]="inventory-repo"
    ["order-microservice"]="order-repo"
    ["payment-microservice"]="payment-repo"
    ["frontend"]="frontend-repo"
)

# 3. LOGIN TO ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REGISTRY_URL

# 4. PROCESS EACH SERVICE
for FOLDER in "${!SERVICES[@]}"; do
    REPO_NAME=${SERVICES[$FOLDER]}
    
    echo "------------------------------------------------"
    echo "Building: $REPO_NAME"

    # Create repo if missing
    aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$REGION" > /dev/null 2>&1 || \
    aws ecr create-repository --repository-name "$REPO_NAME" --region "$REGION"

    # Determine Dockerfile location relative to PROJECT_ROOT
    if [ "$FOLDER" == "frontend" ]; then
        DOCKERFILE="frontend/fargate-deployment/Dockerfile"
    else
        DOCKERFILE="$FOLDER/Dockerfile-ecr"
    fi

    # THE BUILD COMMAND
    # We build from the PROJECT_ROOT so Docker sees all folders
    docker build -t "$REPO_NAME" -f "$DOCKERFILE" .

    if [ $? -eq 0 ]; then
        echo "Pushing $REPO_NAME..."
        docker tag "$REPO_NAME:latest" "$REGISTRY_URL/$REPO_NAME:latest"
        docker push "$REGISTRY_URL/$REPO_NAME:latest"
    else
        echo "FAILED to build $FOLDER. Check if $DOCKERFILE exists."
    fi
done