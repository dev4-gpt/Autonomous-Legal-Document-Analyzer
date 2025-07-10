#!/bin/bash

# Legal Document Analyzer Deployment Script
# This script automates the deployment process for different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="legal-document-analyzer"
DOCKER_IMAGE="legal-analyzer"
DEFAULT_PORT=8501

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    log_info "Python version: $python_version"
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        log_info "Docker version: $docker_version"
    else
        log_warning "Docker not found - Docker deployment will not be available"
    fi
    
    # Check available memory
    if command -v free &> /dev/null; then
        memory_gb=$(free -g | awk '/^Mem:/{print $2}')
        log_info "Available memory: ${memory_gb}GB"
        
        if [ "$memory_gb" -lt 4 ]; then
            log_warning "Less than 4GB RAM available - performance may be impacted"
        fi
    fi
}

setup_environment() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    log_success "Python environment setup complete"
}

setup_configuration() {
    log_info "Setting up configuration..."
    
    # Copy environment template if .env doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Environment file created from template"
            log_warning "Please edit .env file with your configuration"
        else
            log_error ".env.example not found"
            exit 1
        fi
    else
        log_info "Environment file already exists"
    fi
    
    # Create necessary directories
    mkdir -p data/uploads data/analysis data/vectorstore logs
    log_success "Data directories created"
}

run_tests() {
    log_info "Running test suite..."
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    if command -v pytest &> /dev/null; then
        pytest tests/ -v --tb=short
        log_success "All tests passed"
    else
        log_warning "pytest not found - skipping tests"
    fi
}

deploy_local() {
    log_info "Deploying locally..."
    
    check_requirements
    setup_environment
    setup_configuration
    
    if [ "$1" = "--test" ]; then
        run_tests
    fi
    
    log_info "Starting application..."
    source venv/bin/activate
    
    # Check if port is available
    if lsof -Pi :$DEFAULT_PORT -sTCP:LISTEN -t >/dev/null ; then
        log_error "Port $DEFAULT_PORT is already in use"
        exit 1
    fi
    
    # Start the application
    streamlit run app.py --server.port=$DEFAULT_PORT --server.address=0.0.0.0
}

deploy_docker() {
    log_info "Deploying with Docker..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Build Docker image
    log_info "Building Docker image..."
    docker build -t $DOCKER_IMAGE .
    log_success "Docker image built successfully"
    
    # Stop existing container if running
    if [ "$(docker ps -q -f name=$PROJECT_NAME)" ]; then
        log_info "Stopping existing container..."
        docker stop $PROJECT_NAME
        docker rm $PROJECT_NAME
    fi
    
    # Run container
    log_info "Starting Docker container..."
    docker run -d \
        --name $PROJECT_NAME \
        -p $DEFAULT_PORT:$DEFAULT_PORT \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/.env:/app/.env \
        --restart unless-stopped \
        $DOCKER_IMAGE
    
    log_success "Docker container started successfully"
    log_info "Application available at http://localhost:$DEFAULT_PORT"
}

deploy_docker_compose() {
    log_info "Deploying with Docker Compose..."
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        log_error "docker-compose.yml not found"
        exit 1
    fi
    
    # Deploy with Docker Compose
    docker-compose up --build -d
    log_success "Docker Compose deployment complete"
    log_info "Application available at http://localhost:$DEFAULT_PORT"
}

show_status() {
    log_info "Checking application status..."
    
    # Check if running locally
    if lsof -Pi :$DEFAULT_PORT -sTCP:LISTEN -t >/dev/null ; then
        log_success "Application is running on port $DEFAULT_PORT"
    else
        log_info "Application is not running locally"
    fi
    
    # Check Docker container
    if command -v docker &> /dev/null; then
        if [ "$(docker ps -q -f name=$PROJECT_NAME)" ]; then
            log_success "Docker container is running"
            docker ps -f name=$PROJECT_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        else
            log_info "Docker container is not running"
        fi
    fi
}

cleanup() {
    log_info "Cleaning up..."
    
    # Stop Docker container
    if command -v docker &> /dev/null && [ "$(docker ps -q -f name=$PROJECT_NAME)" ]; then
        docker stop $PROJECT_NAME
        docker rm $PROJECT_NAME
        log_success "Docker container stopped and removed"
    fi
    
    # Clean up Docker Compose
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        docker-compose down
        log_success "Docker Compose services stopped"
    fi
    
    # Clean up build artifacts
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "Cleanup complete"
}

show_help() {
    echo "Legal Document Analyzer Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  local           Deploy locally with Python virtual environment"
    echo "  docker          Deploy using Docker container"
    echo "  compose         Deploy using Docker Compose"
    echo "  status          Show application status"
    echo "  cleanup         Clean up deployments and artifacts"
    echo "  help            Show this help message"
    echo ""
    echo "Options:"
    echo "  --test          Run tests before deployment (local only)"
    echo "  --port PORT     Specify port number (default: $DEFAULT_PORT)"
    echo ""
    echo "Examples:"
    echo "  $0 local --test"
    echo "  $0 docker"
    echo "  $0 compose"
    echo "  $0 status"
}

# Main script logic
case "$1" in
    "local")
        deploy_local "$2"
        ;;
    "docker")
        deploy_docker
        ;;
    "compose")
        deploy_docker_compose
        ;;
    "status")
        show_status
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
