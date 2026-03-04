#!/bin/bash

# ============================================
# AUTOMATED ERROR DETECTION & FIXING TOOL
# Real-time monitoring and auto-correction
# ============================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
ERRORS_FIXED=0
WARNINGS=0
TOTAL_CHECKS=0

# Logging functions
log_error() {
    echo -e "${RED}[✗ ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓ FIXED]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠ WARNING]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[ℹ INFO]${NC} $1"
}

log_check() {
    echo -e "${CYAN}[◆ CHECK]${NC} $1"
}

# ============ CHECK 1: ENVIRONMENT FILE ============
check_env_file() {
    log_check "Checking environment file..."
    ((TOTAL_CHECKS++))
    
    if [ ! -f ".env" ]; then
        log_error ".env file not found"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env from template"
            ((ERRORS_FIXED++))
        fi
        return 1
    fi
    
    # Check for required variables
    local required=("TELEGRAM_BOT_TOKEN" "AI_API_KEY" "AI_MODEL")
    for var in "${required[@]}"; do
        if ! grep -q "^${var}=" .env; then
            log_error "Missing required variable: $var"
            ((WARNINGS++))
        fi
    done
}

# ============ CHECK 2: DOCKER COMPOSE SYNTAX ============
check_compose_syntax() {
    log_check "Validating docker-compose.yml syntax..."
    ((TOTAL_CHECKS++))
    
    if ! docker-compose config > /dev/null 2>&1; then
        log_error "Invalid docker-compose.yml syntax"
        docker-compose config 2>&1 | head -5
        return 1
    fi
    log_info "docker-compose.yml syntax is valid"
}

# ============ CHECK 3: DOCKER DAEMON ============
check_docker_daemon() {
    log_check "Checking Docker daemon status..."
    ((TOTAL_CHECKS++))
    
    if ! docker ps > /dev/null 2>&1; then
        log_error "Docker daemon is not running"
        return 1
    fi
    log_info "Docker daemon is running"
}

# ============ CHECK 4: AI MODEL VALIDITY ============
check_ai_model() {
    log_check "Validating AI model configuration..."
    ((TOTAL_CHECKS++))
    
    local ai_model=$(grep "^AI_MODEL=" .env 2>/dev/null | cut -d'=' -f2 || echo "")
    
    if [ -z "$ai_model" ]; then
        log_warning "AI_MODEL not set, setting to default..."
        echo "AI_MODEL=gemini-2.5-flash" >> .env
        ((ERRORS_FIXED++))
        return
    fi
    
    case "$ai_model" in
        gemini-2.5-flash|gpt-4.1-mini|gpt-4.1-nano)
            log_info "AI_MODEL is valid: $ai_model"
            ;;
        *)
            log_error "Invalid AI_MODEL: $ai_model"
            log_success "Auto-fixing to: gemini-2.5-flash"
            sed -i 's/^AI_MODEL=.*/AI_MODEL=gemini-2.5-flash/' .env
            ((ERRORS_FIXED++))
            ;;
    esac
}

# ============ CHECK 5: RESOURCE LIMITS ============
check_resource_limits() {
    log_check "Checking resource limit configuration..."
    ((TOTAL_CHECKS++))
    
    local fixed=0
    
    if ! grep -q "^MEMORY_LIMIT=" .env; then
        log_warning "MEMORY_LIMIT not set, adding default..."
        echo "MEMORY_LIMIT=4096" >> .env
        ((ERRORS_FIXED++))
        ((fixed++))
    fi
    
    if ! grep -q "^CPU_LIMIT=" .env; then
        log_warning "CPU_LIMIT not set, adding default..."
        echo "CPU_LIMIT=2.0" >> .env
        ((ERRORS_FIXED++))
        ((fixed++))
    fi
    
    if [ $fixed -gt 0 ]; then
        log_success "Added $fixed resource limit(s)"
    else
        log_info "Resource limits are configured"
    fi
}

# ============ CHECK 6: CONTAINER HEALTH ============
check_container_health() {
    log_check "Checking container health status..."
    ((TOTAL_CHECKS++))
    
    if ! docker-compose ps > /dev/null 2>&1; then
        log_warning "No running containers found"
        return
    fi
    
    if docker-compose ps | grep -q "healthy"; then
        log_info "Container is healthy"
    elif docker-compose ps | grep -q "unhealthy"; then
        log_error "Container is unhealthy"
        log_info "Attempting to restart..."
        docker-compose restart
        ((ERRORS_FIXED++))
    elif docker-compose ps | grep -q "Up"; then
        log_info "Container is running (health check pending)"
    fi
}

# ============ CHECK 7: LOG FILES ============
check_logs() {
    log_check "Analyzing container logs for errors..."
    ((TOTAL_CHECKS++))
    
    if docker-compose logs 2>/dev/null | grep -i "error" | head -3; then
        ((WARNINGS++))
    else
        log_info "No errors found in logs"
    fi
}

# ============ CHECK 8: DISK SPACE ============
check_disk_space() {
    log_check "Checking available disk space..."
    ((TOTAL_CHECKS++))
    
    local available=$(df /agent/home | tail -1 | awk '{print $4}')
    local threshold=$((1024 * 1024))  # 1GB in KB
    
    if [ "$available" -lt "$threshold" ]; then
        log_error "Low disk space: ${available}KB available"
        ((WARNINGS++))
    else
        log_info "Disk space is sufficient"
    fi
}

# ============ CHECK 9: PORT AVAILABILITY ============
check_port_availability() {
    log_check "Checking if port 8000 is available..."
    ((TOTAL_CHECKS++))
    
    if command -v lsof &> /dev/null; then
        if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
            log_info "Port 8000 is in use (expected if running)"
        else
            log_info "Port 8000 is available"
        fi
    else
        log_info "lsof not available, skipping port check"
    fi
}

# ============ CHECK 10: FILE PERMISSIONS ============
check_permissions() {
    log_check "Checking file permissions..."
    ((TOTAL_CHECKS++))
    
    if [ ! -r ".env" ]; then
        log_error ".env is not readable"
        chmod 644 .env
        ((ERRORS_FIXED++))
    fi
    
    if [ ! -x "deploy.sh" ]; then
        log_warning "deploy.sh is not executable, fixing..."
        chmod +x deploy.sh
        ((ERRORS_FIXED++))
    fi
    
    log_info "File permissions verified"
}

# ============ GENERATE REPORT ============
generate_report() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}         ERROR DETECTION & AUTO-FIX REPORT${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    
    echo ""
    echo -e "Total Checks Run: ${BLUE}${TOTAL_CHECKS}${NC}"
    echo -e "Errors Fixed: ${GREEN}${ERRORS_FIXED}${NC}"
    echo -e "Warnings: ${YELLOW}${WARNINGS}${NC}"
    
    echo ""
    if [ $ERRORS_FIXED -gt 0 ]; then
        echo -e "${GREEN}✓ Fixed ${ERRORS_FIXED} error(s)${NC}"
    fi
    
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ ${WARNINGS} warning(s) require attention${NC}"
    fi
    
    if [ $ERRORS_FIXED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ All systems operational!${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    
    # Recommendation
    if [ $ERRORS_FIXED -gt 0 ] || [ $WARNINGS -gt 0 ]; then
        echo ""
        log_info "Recommendation: Run './deploy.sh' to apply all fixes"
    fi
}

# ============ MAIN EXECUTION ============
main() {
    log_info "════════════════════════════════════════════════════"
    log_info "AUTOMATED ERROR DETECTION & AUTO-FIX TOOL"
    log_info "════════════════════════════════════════════════════"
    echo ""
    
    # Run all checks
    check_env_file
    check_compose_syntax
    check_docker_daemon
    check_ai_model
    check_resource_limits
    check_container_health
    check_logs
    check_disk_space
    check_port_availability
    check_permissions
    
    # Generate report
    generate_report
}

# Execute main function
main "$@"
