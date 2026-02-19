#!/bin/bash

# Deployment script for Airflow Monitoring System
# Usage: ./scripts/deploy.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
PROJECT_NAME="airflow-monitoring"
IMAGE_TAG=${GITHUB_SHA:-latest}
REGISTRY="ghcr.io/hellofresh"

echo "🚀 Starting deployment to $ENVIRONMENT environment..."

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo "❌ Error: Environment must be 'staging' or 'production'"
    exit 1
fi

# Check required tools
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed."; exit 1; }

# Set environment-specific variables
if [[ "$ENVIRONMENT" == "production" ]]; then
    COMPOSE_FILE="docker-compose.yml"
    ENV_FILE=".env.production"
    REPLICAS=3
else
    COMPOSE_FILE="docker-compose.staging.yml"
    ENV_FILE=".env.staging"
    REPLICAS=1
fi

echo "📋 Configuration:"
echo "  Environment: $ENVIRONMENT"
echo "  Image: $REGISTRY/$PROJECT_NAME:$IMAGE_TAG"
echo "  Compose file: $COMPOSE_FILE"
echo "  Replicas: $REPLICAS"

# Check if environment file exists
if [[ ! -f "$ENV_FILE" ]]; then
    echo "❌ Environment file $ENV_FILE not found"
    exit 1
fi

# Pull latest images
echo "📥 Pulling latest images..."
docker pull "$REGISTRY/$PROJECT_NAME:$IMAGE_TAG"

# Stop existing containers gracefully
echo "🛑 Stopping existing containers..."
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down --timeout 30

# Start new containers
echo "🔄 Starting new containers..."
export IMAGE_TAG
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --scale airflow-monitor=$REPLICAS

# Wait for services to be healthy
echo "🔍 Waiting for services to be healthy..."
sleep 30

# Health check
echo "🩺 Running health checks..."
for i in {1..5}; do
    if docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps | grep -q "Up (healthy)"; then
        echo "✅ Services are healthy"
        break
    elif [[ $i -eq 5 ]]; then
        echo "❌ Health check failed after 5 attempts"
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs
        exit 1
    else
        echo "⏳ Attempt $i/5 - waiting for services to be ready..."
        sleep 30
    fi
done

# Clean up old images
echo "🧹 Cleaning up old images..."
docker image prune -f --filter "until=168h"

echo "✅ Deployment to $ENVIRONMENT completed successfully!"

# Show running services
echo "📊 Running services:"
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps