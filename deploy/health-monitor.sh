#!/bin/bash

# ============================================
# CONTINUOUS HEALTH MONITORING
# Real-time container and system health checks
# ============================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CHECK_INTERVAL=60  # seconds
MAX_FAILURES=3
FAILURE_COUNT=0

# Logging
log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# ============ CONTAINER HEALTH CHECK ============
check_container_health() {
    if ! docker-compose ps | grep -q "healthy"; then
        if docker-compose ps | grep -q "unhealthy"; then
            log_error "Container is unhealthy"
            FAILURE_COUNT=$((FAILURE_COUNT + 1))
            return 1
        fi
    fi
    log_success "Container is healthy"
    FAILURE_COUNT=0
    return 0
}

# ============ AUTO-RESTART ON FAILURE ============
auto_restart() {
    if [ $FAILURE_COUNT -ge $MAX_FAILURES ]; then
        log_warning "Max failures reached, attempting restart..."
        
        # Stop containers
        docker-compose down
        sleep 5
        
        # Run error checker
        if [ -f "error-checker.sh" ]; then
            log_info "Running error checker..."
            bash error-checker.sh
        fi
        
        # Restart containers
        log_info "Restarting containers..."
        docker-compose up -d
        
        sleep 10
        FAILURE_COUNT=0
    fi
}

# ============ RESOURCE MONITORING ============
monitor_resources() {
    log_info "Monitoring resource usage..."
    
    local memory_limit=$(grep "MEMORY_LIMIT=" .env 2>/dev/null | cut -d'=' -f2 || echo "4096")
    local memory_threshold=$((memory_limit * 80 / 100))  # 80% warning threshold
    
    # Get actual memory usage
    local memory_usage=$(docker stats --no-stream vm-telegram-bot 2>/dev/null | awk 'NR==2 {print $4}' | sed 's/MiB//' || echo "0")
    
    if (( $(echo "$memory_usage > $memory_threshold" | bc -l 2>/dev/null || echo 0) )); then
        log_warning "High memory usage: ${memory_usage}MiB / ${memory_limit}MiB"
    else
        log_info "Memory usage: ${memory_usage}MiB / ${memory_limit}MiB"
    fi
}

# ============ LOG ANALYSIS ============
analyze_logs() {
    log_info "Analyzing recent logs..."
    
    # Check for recent errors
    local error_count=$(docker-compose logs --tail=50 2>/dev/null | grep -i "error" | wc -l || echo "0")
    
    if [ "$error_count" -gt 0 ]; then
        log_warning "Found $error_count error(s) in recent logs"
        docker-compose logs --tail=5 2>/dev/null | grep -i "error" || true
    else
        log_info "No errors in recent logs"
    fi
}

# ============ PORT CONNECTIVITY CHECK ============
check_port_connectivity() {
    log_info "Checking port 8000 connectivity..."
    
    if command -v curl &> /dev/null; then
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log_success "Port 8000 is responding"
        else
            log_warning "Port 8000 is not responding to health check"
        fi
    else
        log_info "curl not available, skipping connectivity check"
    fi
}

# ============ MAIN MONITORING LOOP ============
main() {
    log_info "════════════════════════════════════════════════════"
    log_info "CONTINUOUS HEALTH MONITORING STARTED"
    log_info "Check interval: ${CHECK_INTERVAL}s"
    log_info "════════════════════════════════════════════════════"
    echo ""
    
    while true; do
        log_info "─── Health Check Cycle ───"
        
        # Run all checks
        check_container_health || true
        monitor_resources
        analyze_logs
        check_port_connectivity
        auto_restart
        
        log_info "Waiting ${CHECK_INTERVAL}s for next check..."
        echo ""
        sleep $CHECK_INTERVAL
    done
}

# Trap for graceful shutdown
trap 'log_info "Monitoring stopped"; exit 0' SIGINT SIGTERM

# Execute main loop
main "$@"
