#!/bin/bash
# ==============================================================================
# MasterX - Development Environment Management Script
# ==============================================================================
# Convenient wrapper for Docker Compose development commands
# Following Big Tech standards for developer experience
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Docker compose file
COMPOSE_FILE="docker-compose.dev.yml"

# Functions
print_header() {
    echo -e "${BLUE}===============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===============================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_env() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        echo ""
        echo "Please create .env file from template:"
        echo "  cp .env.docker.example .env"
        echo ""
        echo "Then edit .env and add your API keys."
        exit 1
    fi
}

# Command handlers
case "${1:-}" in
    start|up)
        print_header "Starting MasterX Development Environment"
        check_env
        docker-compose -f $COMPOSE_FILE up -d
        print_success "Services started successfully!"
        echo ""
        echo "📊 Access points:"
        echo "   Frontend:  http://localhost:3000"
        echo "   Backend:   http://localhost:8001"
        echo "   API Docs:  http://localhost:8001/docs"
        echo "   MongoDB:   mongodb://localhost:27017"
        echo ""
        echo "📝 View logs: ./docker-dev.sh logs"
        ;;
    
    stop|down)
        print_header "Stopping MasterX Development Environment"
        docker-compose -f $COMPOSE_FILE down
        print_success "Services stopped successfully!"
        ;;
    
    restart)
        print_header "Restarting MasterX Development Environment"
        docker-compose -f $COMPOSE_FILE restart
        print_success "Services restarted successfully!"
        ;;
    
    build)
        print_header "Building Docker Images"
        check_env
        docker-compose -f $COMPOSE_FILE build --no-cache
        print_success "Images built successfully!"
        ;;
    
    rebuild)
        print_header "Rebuilding and Starting Services"
        check_env
        docker-compose -f $COMPOSE_FILE down
        docker-compose -f $COMPOSE_FILE build --no-cache
        docker-compose -f $COMPOSE_FILE up -d
        print_success "Services rebuilt and started!"
        ;;
    
    logs)
        SERVICE="${2:-}"
        if [ -z "$SERVICE" ]; then
            docker-compose -f $COMPOSE_FILE logs -f
        else
            docker-compose -f $COMPOSE_FILE logs -f "$SERVICE"
        fi
        ;;
    
    ps|status)
        print_header "Service Status"
        docker-compose -f $COMPOSE_FILE ps
        ;;
    
    shell)
        SERVICE="${2:-backend}"
        print_header "Opening Shell in $SERVICE Container"
        docker-compose -f $COMPOSE_FILE exec "$SERVICE" sh
        ;;
    
    clean)
        print_header "Cleaning Up Docker Resources"
        print_warning "This will remove containers, networks, and volumes!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f $COMPOSE_FILE down -v
            print_success "Cleanup complete!"
        else
            print_warning "Cleanup cancelled"
        fi
        ;;
    
    health)
        print_header "Health Check"
        echo "🔍 Checking service health..."
        echo ""
        echo "Backend API:"
        curl -s http://localhost:8001/api/health | python3 -m json.tool || print_error "Backend not responding"
        echo ""
        echo "Frontend:"
        curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:3000 || print_error "Frontend not responding"
        ;;
    
    help|--help|-h|"")
        print_header "MasterX Development Environment - Docker Management"
        echo ""
        echo "Usage: ./docker-dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start, up      Start all services"
        echo "  stop, down     Stop all services"
        echo "  restart        Restart all services"
        echo "  build          Build Docker images"
        echo "  rebuild        Rebuild images and restart services"
        echo "  logs [service] View logs (optionally for specific service)"
        echo "  ps, status     Show service status"
        echo "  shell [service] Open shell in container (default: backend)"
        echo "  clean          Remove all containers, networks, and volumes"
        echo "  health         Check service health"
        echo "  help           Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./docker-dev.sh start          # Start all services"
        echo "  ./docker-dev.sh logs backend   # View backend logs"
        echo "  ./docker-dev.sh shell frontend # Open shell in frontend"
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Run './docker-dev.sh help' for usage information"
        exit 1
        ;;
esac
