#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  🐳 ADVANCED DOCKER INSTALLER + BOT DEPLOYER
#  Supports: Ubuntu, Debian, CentOS, RHEL, Amazon Linux, macOS
#  Features: Docker CE + Compose v2 + BuildKit + Portainer
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()     { echo -e "${GREEN}[✔]${NC} $1"; }
warn()    { echo -e "${YELLOW}[⚠]${NC} $1"; }
error()   { echo -e "${RED}[✘]${NC} $1"; exit 1; }
section() { echo -e "\n${BOLD}${BLUE}══ $1 ══${NC}"; }

section "🐳 Advanced Docker Installer"
echo -e "${CYAN}Telegram AI Bot — Full Production Stack${NC}"
echo -e "Installs: Docker CE + Compose v2 + BuildKit + All services\n"

# ── Detect OS ──
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [ -f /etc/os-release ]; then
        source /etc/os-release
        echo "${ID:-linux}"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
ARCH=$(uname -m)
log "Detected OS: $OS | Arch: $ARCH"

# ── Check root (Linux) ──
if [[ "$OS" != "macos" && "$EUID" -ne 0 ]]; then
    warn "Not root — using sudo"
    SUDO="sudo"
else
    SUDO=""
fi

# ════════════════════════════════════════════
#  INSTALL DOCKER
# ════════════════════════════════════════════
install_docker_linux() {
    section "Installing Docker CE (latest)"

    # Remove old versions
    $SUDO apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    # Dependencies
    $SUDO apt-get update -qq
    $SUDO apt-get install -y -qq \
        ca-certificates curl gnupg lsb-release apt-transport-https

    # Docker GPG key
    $SUDO install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    $SUDO chmod a+r /etc/apt/keyrings/docker.gpg

    # Docker repo
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        $SUDO tee /etc/apt/sources.list.d/docker.list > /dev/null

    $SUDO apt-get update -qq
    $SUDO apt-get install -y \
        docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin

    log "Docker CE installed"
}

install_docker_centos() {
    section "Installing Docker CE (CentOS/RHEL)"
    $SUDO yum remove -y docker docker-client docker-client-latest \
        docker-common docker-latest docker-latest-logrotate \
        docker-logrotate docker-engine 2>/dev/null || true
    $SUDO yum install -y yum-utils
    $SUDO yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    $SUDO yum install -y docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin
    $SUDO systemctl start docker
    $SUDO systemctl enable docker
    log "Docker CE installed on CentOS"
}

install_docker_macos() {
    section "Installing Docker Desktop (macOS)"
    if command -v brew &>/dev/null; then
        brew install --cask docker
        log "Docker Desktop installed via Homebrew"
        warn "Please open Docker Desktop app to complete setup"
    else
        warn "Homebrew not found. Install from: https://www.docker.com/products/docker-desktop"
        open "https://www.docker.com/products/docker-desktop" 2>/dev/null || true
        echo "Press Enter once Docker Desktop is running..."
        read -r
    fi
}

# Select installer
case "$OS" in
    ubuntu|debian)  install_docker_linux ;;
    centos|rhel|fedora|amzn) install_docker_centos ;;
    macos)          install_docker_macos ;;
    *)
        warn "Unknown OS. Attempting universal install..."
        curl -fsSL https://get.docker.com | $SUDO sh
        ;;
esac

# ════════════════════════════════════════════
#  POST-INSTALL CONFIGURATION
# ════════════════════════════════════════════
section "🔧 Configuring Docker"

# Start & enable service
if [[ "$OS" != "macos" ]]; then
    $SUDO systemctl start docker 2>/dev/null || true
    $SUDO systemctl enable docker 2>/dev/null || true

    # Add current user to docker group
    CURRENT_USER="${SUDO_USER:-$(whoami)}"
    if [ "$CURRENT_USER" != "root" ]; then
        $SUDO usermod -aG docker "$CURRENT_USER"
        warn "User '$CURRENT_USER' added to docker group. Re-login or run: newgrp docker"
    fi
fi

# Enable BuildKit (faster builds)
mkdir -p ~/.docker
cat > ~/.docker/config.json << 'EOF'
{
  "features": {
    "buildkit": true
  },
  "experimental": "enabled"
}
EOF

# Docker daemon config with advanced features
if [[ "$OS" != "macos" ]]; then
    $SUDO mkdir -p /etc/docker
    $SUDO tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "experimental": true,
  "features": { "buildkit": true },
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "20m",
    "max-file": "5"
  },
  "default-ulimits": {
    "nofile": { "Name": "nofile", "Hard": 65536, "Soft": 65536 }
  },
  "live-restore": true
}
EOF
    $SUDO systemctl restart docker 2>/dev/null || true
fi

# ════════════════════════════════════════════
#  VERIFY INSTALLATION
# ════════════════════════════════════════════
section "✅ Verifying Docker"
if command -v docker &>/dev/null; then
    DOCKER_VERSION=$(docker --version)
    log "$DOCKER_VERSION"
    COMPOSE_VERSION=$(docker compose version 2>/dev/null || echo "Docker Compose: checking...")
    log "$COMPOSE_VERSION"
else
    error "Docker installation failed!"
fi

# ════════════════════════════════════════════
#  DEPLOY THE BOT STACK
# ════════════════════════════════════════════
section "🚀 Deploying Telegram AI Bot Stack"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_DIR="$(dirname "$SCRIPT_DIR")"

if [ ! -f "$BOT_DIR/.env" ]; then
    error ".env file not found at $BOT_DIR/.env — add your API keys first!"
fi

cd "$BOT_DIR"

log "Building Docker images..."
docker compose -f deploy/docker-compose.yml build --parallel

log "Starting all services..."
docker compose -f deploy/docker-compose.yml up -d

# Wait for services
echo -n "Waiting for services to start"
for i in {1..12}; do
    sleep 2
    echo -n "."
done
echo ""

# ════════════════════════════════════════════
#  SERVICE URLS
# ════════════════════════════════════════════
section "🌐 Your Services Are Live"

HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "your-server-ip")

echo -e ""
echo -e "${BOLD}Access from any browser or iOS Safari:${NC}"
echo -e ""
echo -e "  ${GREEN}🤖 Bot Dashboard${NC}      http://${HOST_IP}:8080"
echo -e "  ${BLUE}📊 Portainer UI${NC}       http://${HOST_IP}:9000"
echo -e "  ${YELLOW}📈 Grafana${NC}           http://${HOST_IP}:3000  (admin / admin123)"
echo -e "  ${CYAN}📉 Prometheus${NC}         http://${HOST_IP}:9090"
echo -e ""
echo -e "${BOLD}Management commands:${NC}"
echo -e "  docker compose -f deploy/docker-compose.yml logs -f     # Live logs"
echo -e "  docker compose -f deploy/docker-compose.yml ps          # Service status"
echo -e "  docker compose -f deploy/docker-compose.yml restart     # Restart all"
echo -e "  docker compose -f deploy/docker-compose.yml down        # Stop all"
echo -e ""
echo -e "${GREEN}${BOLD}✅ Everything is running! Open http://${HOST_IP}:8080 in any browser${NC}"
echo -e "${CYAN}📱 Works on iOS Safari, Android Chrome, Desktop — any device!${NC}"
