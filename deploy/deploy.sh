#!/bin/bash

# ============================================
# TELEGRAM BOT DEPLOYMENT SCRIPT
# WITH AUTOMATIC ERROR DETECTION & FIXING
# ============================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# ============ ERROR HANDLING FUNCTION ============
handle_error() {
    local line_number=$1
    local error_code=$2
    log_error "Deployment failed at line $line_number with exit code $error_code"
    
    # Rollback
    log_info "Rolling back changes..."
    docker-compose down 2>/dev/null || true
    
    exit "$error_code"
}

trap 'handle_error ${LINENO} $?' ERR

# ============ PRE-DEPLOYMENT VALIDATION ============
validate_environment() {
    log_info "Validating environment..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_warning ".env file not found! Creating from template..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warning "Created .env from .env.example - PLEASE UPDATE WITH YOUR CREDENTIALS!"
        else
            log_error ".env.example not found"
            exit 1
        fi
    fi
    
    # Validate required environment variables
    local required_vars=("TELEGRAM_BOT_TOKEN" "AI_API_KEY" "AI_MODEL")
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env; then
            log_error "Required variable $var not found in .env"
            exit 1
        fi
    done
    
    log_success "Environment validation passed"
}

# ============ AUTO-ERROR DETECTION ============
detect_and_fix_errors() {
    log_info "Running automatic error detection..."
    
    local errors_found=0
    
    # ERROR 1: Check AI_MODEL validity
    local ai_model=$(grep "^AI_MODEL=" .env | cut -d'=' -f2)
    case "$ai_model" in
        gemini-2.5-flash|gpt-4.1-mini|gpt-4.1-nano)
            log_success "AI_MODEL is valid: $ai_model"
            ;;
        *)
            log_error "Invalid AI_MODEL: $ai_model"
            log_info "Auto-fixing: Defaulting to gemini-2.5-flash"
            sed -i 's/^AI_MODEL=.*/AI_MODEL=gemini-2.5-flash/' .env
            ((errors_found++))
            ;;
    esac
    
    # ERROR 2: Check if memory limit is set
    if ! grep -q "^MEMORY_LIMIT=" .env; then
        log_warning "MEMORY_LIMIT not set, auto-fixing..."
        echo "MEMORY_LIMIT=4096" >> .env
        ((errors_found++))
    fi
    
    # ERROR 3: Check if CPU limit is set
    if ! grep -q "^CPU_LIMIT=" .env; then
        log_warning "CPU_LIMIT not set, auto-fixing..."
        echo "CPU_LIMIT=2.0" >> .env
        ((errors_found++))
    fi
    
    # ERROR 4: Validate docker-compose.yml syntax
    if ! docker-compose config > /dev/null 2>&1; then
        log_error "docker-compose.yml has syntax errors"
        docker-compose config
        exit 1
    fi
    log_success "docker-compose.yml syntax is valid"
    
    # ERROR 5: Check Docker daemon is running
    if ! docker ps > /dev/null 2>&1; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    log_success "Docker daemon is running"
    
    if [ $errors_found -gt 0 ]; then
        log_warning "Fixed $errors_found automatic error(s)"
    else
        log_success "No errors detected"
    fi
}

# ============ DEPLOYMENT FUNCTION ============
deploy() {
    log_info "Starting deployment..."
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose down 2>/dev/null || true
    
    # Build and start new containers
    log_info "Building and starting containers..."
    docker-compose up -d
    
    # Wait for container to be healthy
    log_info "Waiting for container health check..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps | grep -q "healthy"; then
            log_success "Container is healthy"
            break
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "Container failed to become healthy"
        docker-compose logs
        exit 1
    fi
    
    log_success "Deployment completed successfully"
}

# ============ VERIFICATION ============
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check if container is running
    if ! docker-compose ps | grep -q "Up"; then
        log_error "Container is not running"
        exit 1
    fi
    
    # Check logs for errors
    if docker-compose logs | grep -i "error"; then
        log_warning "Errors found in container logs (see above)"
    fi
    
    log_success "Deployment verification passed"
}

# ============ MAIN EXECUTION ============
main() {
    log_info "════════════════════════════════════════════════════"
    log_info "TELEGRAM BOT DEPLOYMENT SCRIPT"
    log_info "════════════════════════════════════════════════════"
    
    validate_environment
    detect_and_fix_errors
    deploy
    verify_deployment
    
    log_success "════════════════════════════════════════════════════"
    log_success "DEPLOYMENT COMPLETED SUCCESSFULLY!"
    log_success "════════════════════════════════════════════════════"
    
    echo ""
    log_info "Container Status:"
    docker-compose ps
    
    echo ""
    log_info "To view logs: docker-compose logs -f"
    log_info "To stop: docker-compose down"
}

# Run main function
main "$@"
