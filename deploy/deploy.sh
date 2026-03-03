#!/bin/bash

set -euo pipefail

# Configuration
DOCKER_REGISTRY=${DOCKER_REGISTRY:-docker.io}
DOCKER_USERNAME=${DOCKER_USERNAME:-}
DOCKER_PASSWORD=${DOCKER_PASSWORD:-}
IMAGE_NAME=${IMAGE_NAME:-telegram-ai-bot}
CONTAINER_NAME=${CONTAINER_NAME:-telegram-ai-bot}
ENVIRONMENT=${ENVIRONMENT:-production}
LOG_FILE="deploy-$(date +%Y%m%d-%H%M%S).log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    command -v docker &> /dev/null || error "Docker is not installed"
    command -v docker-compose &> /dev/null || error "Docker Compose is not installed"
    
    log "✓ All prerequisites met"
}

# Load environment
load_environment() {
    log "Loading environment from .env..."
    
    if [ ! -f ".env" ]; then
        error ".env file not found. Create it from .env.example"
    fi
    
    set -a
    source .env
    set +a
    
    log "✓ Environment loaded"
}

# Login to Docker registry
docker_login() {
    if [ -z "$DOCKER_USERNAME" ] || [ -z "$DOCKER_PASSWORD" ]; then
        warning "Docker credentials not set. Skipping login."
        return
    fi
    
    log "Logging in to Docker registry..."
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin "$DOCKER_REGISTRY" || error "Docker login failed"
    log "✓ Docker login successful"
}

# Pull latest images
pull_images() {
    log "Pulling latest Docker images..."
    docker-compose pull || error "Failed to pull images"
    log "✓ Images pulled successfully"
}

# Stop existing container
stop_container() {
    log "Stopping existing container..."
    docker-compose down || warning "Failed to stop container (may not exist)"
    log "✓ Container stopped"
}

# Start new container
start_container() {
    log "Starting container..."
    docker-compose up -d || error "Failed to start container"
    log "✓ Container started"
}

# Health check
health_check() {
    log "Performing health check..."
    
    sleep 5
    
    for i in {1..5}; do
        if docker-compose ps | grep -q "$CONTAINER_NAME.*Up"; then
            log "✓ Container is healthy"
            return 0
        fi
        
        if [ $i -lt 5 ]; then
            warning "Health check $i/5 failed, retrying..."
            sleep 5
        fi
    done
    
    error "Container failed health check"
}

# Show logs
show_logs() {
    log "Showing recent logs..."
    docker-compose logs --tail=50 || warning "Failed to retrieve logs"
}

# Main deployment
main() {
    log "Starting deployment for $ENVIRONMENT environment..."
    
    check_prerequisites
    load_environment
    docker_login
    pull_images
    stop_container
    start_container
    health_check
    show_logs
    
    log "✓ Deployment completed successfully!"
    log "Container status:"
    docker-compose ps
}

# Trap errors
trap 'error "Deployment failed"' ERR

# Run main
main "$@"