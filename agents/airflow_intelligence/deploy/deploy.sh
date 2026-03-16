#!/bin/bash
#
# Deployment script for Airflow Intelligence Agent
#
# Usage:
#   ./deploy.sh docker      # Deploy using Docker Compose
#   ./deploy.sh systemd     # Deploy as systemd service
#   ./deploy.sh k8s         # Deploy to Kubernetes
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env() {
    if [ ! -f "$PROJECT_ROOT/agents/airflow_intelligence/.env" ]; then
        error ".env file not found at agents/airflow_intelligence/.env"
        warn "Please create .env file with your credentials before deploying"
        exit 1
    fi
}

# Docker deployment - Note: Requires docker-compose.yml in project root
deploy_docker() {
    error "Docker Compose deployment not configured"
    info "Use Systemd or Kubernetes deployment instead"
    info "Or build Docker image manually:"
    info "  cd agents/airflow_intelligence/deploy"
    info "  docker build -t airflow-intelligence-agent ."
    info "  docker run -d --env-file ../.env airflow-intelligence-agent"
    exit 1
}

# Systemd deployment
deploy_systemd() {
    info "Deploying as systemd service..."

    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        error "Please run as root (use sudo)"
        exit 1
    fi

    INSTALL_DIR="/opt/airflow-intelligence-agent"

    # Create user
    info "Creating agent user..."
    id -u agent &>/dev/null || useradd -r -s /bin/false agent

    # Create installation directory
    info "Creating installation directory..."
    mkdir -p "$INSTALL_DIR"
    cp -r "$PROJECT_ROOT/agents" "$INSTALL_DIR/"

    # Create virtual environment
    info "Setting up virtual environment..."
    cd "$INSTALL_DIR"
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r agents/airflow_intelligence/requirements.txt

    # Create memory directory
    mkdir -p "$INSTALL_DIR/.agent_memory"

    # Set permissions
    chown -R agent:agent "$INSTALL_DIR"

    # Install systemd service
    info "Installing systemd service..."
    cp "$SCRIPT_DIR/systemd/airflow-intelligence-agent.service" /etc/systemd/system/
    systemctl daemon-reload

    # Start service
    info "Starting service..."
    systemctl enable airflow-intelligence-agent
    systemctl start airflow-intelligence-agent

    info "Deployment complete!"
    info "Check status: systemctl status airflow-intelligence-agent"
    info "View logs: journalctl -u airflow-intelligence-agent -f"
    info "Stop: systemctl stop airflow-intelligence-agent"
}

# Kubernetes deployment
deploy_k8s() {
    info "Deploying to Kubernetes..."

    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        error "kubectl not found. Please install kubectl."
        exit 1
    fi

    # Build and push image
    warn "Make sure to build and push the Docker image first:"
    warn "  docker build -t your-registry/airflow-intelligence-agent:latest ."
    warn "  docker push your-registry/airflow-intelligence-agent:latest"
    warn ""
    read -p "Have you built and pushed the image? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi

    # Apply manifests
    info "Applying Kubernetes manifests..."
    kubectl apply -f "$SCRIPT_DIR/kubernetes/deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/kubernetes/cronjob.yaml"

    info "Deployment complete!"
    info "Check status: kubectl get pods -n airflow-intelligence"
    info "View logs: kubectl logs -f -n airflow-intelligence deployment/airflow-intelligence-agent"
}

# Main
main() {
    check_env

    case "${1:-}" in
        systemd)
            deploy_systemd
            ;;
        k8s|kubernetes)
            deploy_k8s
            ;;
        docker)
            deploy_docker
            ;;
        *)
            echo "Usage: $0 {systemd|k8s}"
            echo ""
            echo "Deployment options:"
            echo "  systemd  - Deploy as systemd service (Linux servers) [Recommended]"
            echo "  k8s      - Deploy to Kubernetes (production)"
            echo ""
            echo "For Docker, build manually:"
            echo "  cd deploy && docker build -t airflow-intelligence-agent ."
            exit 1
            ;;
    esac
}

main "$@"
