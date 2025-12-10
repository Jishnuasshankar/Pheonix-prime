#!/bin/bash
# ==============================================================================
# MasterX - UV Package Manager Helper Script
# ==============================================================================
# Convenient wrapper for UV operations on MasterX backend
# ==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Paths
BACKEND_DIR="/app/backend"
VENV_PYTHON="/root/.venv/bin/python"
UV_BIN="/root/.local/bin/uv"
REQUIREMENTS="$BACKEND_DIR/requirements.txt"

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

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

check_uv() {
    if [ ! -f "$UV_BIN" ]; then
        print_error "UV not found at $UV_BIN"
        echo ""
        echo "Install UV with:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
}

# Command handlers
case "${1:-}" in
    install)
        print_header "Installing Package with UV"
        check_uv
        
        if [ -z "$2" ]; then
            print_error "Package name required"
            echo "Usage: $0 install <package>[==version]"
            exit 1
        fi
        
        print_info "Installing: $2"
        cd "$BACKEND_DIR"
        $UV_BIN pip install --python "$VENV_PYTHON" "$2"
        print_success "Package installed: $2"
        
        print_warning "Don't forget to update requirements.txt:"
        echo "  $0 freeze"
        ;;
    
    uninstall)
        print_header "Uninstalling Package with UV"
        check_uv
        
        if [ -z "$2" ]; then
            print_error "Package name required"
            echo "Usage: $0 uninstall <package>"
            exit 1
        fi
        
        print_info "Uninstalling: $2"
        cd "$BACKEND_DIR"
        $UV_BIN pip uninstall --python "$VENV_PYTHON" "$2"
        print_success "Package uninstalled: $2"
        
        print_warning "Don't forget to update requirements.txt:"
        echo "  $0 freeze"
        ;;
    
    sync)
        print_header "Syncing Environment with requirements.txt"
        check_uv
        
        print_info "Syncing from: $REQUIREMENTS"
        cd "$BACKEND_DIR"
        
        START_TIME=$(date +%s)
        $UV_BIN pip sync --python "$VENV_PYTHON" requirements.txt
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        
        print_success "Environment synced in ${DURATION}s"
        
        read -p "Restart backend? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo supervisorctl restart backend
            print_success "Backend restarted"
        fi
        ;;
    
    freeze)
        print_header "Freezing Current Environment"
        check_uv
        
        print_info "Generating requirements.txt from current environment"
        cd "$BACKEND_DIR"
        
        # Backup existing requirements
        if [ -f requirements.txt ]; then
            cp requirements.txt requirements.txt.backup
            print_info "Backed up to requirements.txt.backup"
        fi
        
        $UV_BIN pip freeze --python "$VENV_PYTHON" > requirements.txt
        
        PACKAGE_COUNT=$(cat requirements.txt | wc -l)
        print_success "Frozen $PACKAGE_COUNT packages to requirements.txt"
        ;;
    
    list)
        print_header "Installed Packages"
        check_uv
        
        cd "$BACKEND_DIR"
        $UV_BIN pip list --python "$VENV_PYTHON"
        ;;
    
    show)
        print_header "Package Information"
        check_uv
        
        if [ -z "$2" ]; then
            print_error "Package name required"
            echo "Usage: $0 show <package>"
            exit 1
        fi
        
        cd "$BACKEND_DIR"
        $UV_BIN pip show --python "$VENV_PYTHON" "$2"
        ;;
    
    upgrade)
        print_header "Upgrading Package"
        check_uv
        
        if [ -z "$2" ]; then
            print_error "Package name required"
            echo "Usage: $0 upgrade <package>"
            exit 1
        fi
        
        print_info "Upgrading: $2"
        cd "$BACKEND_DIR"
        $UV_BIN pip install --upgrade --python "$VENV_PYTHON" "$2"
        print_success "Package upgraded: $2"
        
        print_warning "Don't forget to update requirements.txt:"
        echo "  $0 freeze"
        ;;
    
    search)
        print_header "Searching Packages"
        
        if [ -z "$2" ]; then
            print_error "Search term required"
            echo "Usage: $0 search <term>"
            exit 1
        fi
        
        print_info "Searching installed packages for: $2"
        cd "$BACKEND_DIR"
        $UV_BIN pip list --python "$VENV_PYTHON" | grep -i "$2"
        ;;
    
    verify)
        print_header "Verifying Installation"
        check_uv
        
        print_info "Checking UV version"
        $UV_BIN --version
        
        print_info "Checking virtual environment"
        if [ -f "$VENV_PYTHON" ]; then
            print_success "Virtual environment found: $VENV_PYTHON"
            $VENV_PYTHON --version
        else
            print_error "Virtual environment not found: $VENV_PYTHON"
            exit 1
        fi
        
        print_info "Checking installed packages"
        PACKAGE_COUNT=$($UV_BIN pip list --python "$VENV_PYTHON" | tail -n +3 | wc -l)
        print_success "$PACKAGE_COUNT packages installed"
        
        print_info "Checking critical packages"
        CRITICAL_PACKAGES=("fastapi" "uvicorn" "motor" "torch" "openai" "transformers")
        
        for pkg in "${CRITICAL_PACKAGES[@]}"; do
            if $UV_BIN pip show --python "$VENV_PYTHON" "$pkg" > /dev/null 2>&1; then
                VERSION=$($UV_BIN pip show --python "$VENV_PYTHON" "$pkg" | grep Version | awk '{print $2}')
                print_success "$pkg installed (v$VERSION)"
            else
                print_error "$pkg NOT installed"
            fi
        done
        
        print_info "Checking backend service"
        if sudo supervisorctl status backend | grep -q RUNNING; then
            print_success "Backend service is running"
        else
            print_warning "Backend service is not running"
        fi
        ;;
    
    benchmark)
        print_header "UV vs PIP Benchmark"
        check_uv
        
        print_warning "This will test installation speed (requires temp venv)"
        read -p "Continue? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
        
        TEST_DIR="/tmp/uv-benchmark"
        rm -rf "$TEST_DIR"
        mkdir -p "$TEST_DIR"
        cd "$TEST_DIR"
        
        # Create test requirements (subset of packages)
        cat > test-requirements.txt << EOF
fastapi==0.110.1
uvicorn==0.25.0
pydantic==2.11.9
httpx==0.28.1
motor==3.3.1
EOF
        
        # Benchmark UV
        print_info "Testing UV..."
        python -m venv venv-uv
        START_TIME=$(date +%s%3N)
        $UV_BIN pip install --python venv-uv/bin/python -r test-requirements.txt > /dev/null 2>&1
        END_TIME=$(date +%s%3N)
        UV_TIME=$((END_TIME - START_TIME))
        
        # Benchmark pip
        print_info "Testing pip..."
        python -m venv venv-pip
        START_TIME=$(date +%s%3N)
        venv-pip/bin/pip install -r test-requirements.txt > /dev/null 2>&1
        END_TIME=$(date +%s%3N)
        PIP_TIME=$((END_TIME - START_TIME))
        
        # Results
        echo ""
        print_header "Benchmark Results (5 packages)"
        echo -e "${CYAN}UV:${NC}  ${UV_TIME}ms"
        echo -e "${CYAN}PIP:${NC} ${PIP_TIME}ms"
        
        SPEEDUP=$((PIP_TIME / UV_TIME))
        echo ""
        print_success "UV is ${SPEEDUP}x faster than pip!"
        
        rm -rf "$TEST_DIR"
        ;;
    
    clean)
        print_header "Cleaning UV Cache"
        check_uv
        
        print_warning "This will clear UV's package cache"
        read -p "Continue? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            $UV_BIN cache clean
            print_success "UV cache cleaned"
        fi
        ;;
    
    help|--help|-h|"")
        print_header "MasterX UV Package Manager"
        echo ""
        echo "Fast Python package management using UV (10-100x faster than pip)"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  ${GREEN}install <pkg>${NC}     Install a package (e.g., install fastapi==0.110.0)"
        echo "  ${GREEN}uninstall <pkg>${NC}   Uninstall a package"
        echo "  ${GREEN}upgrade <pkg>${NC}     Upgrade a package to latest version"
        echo "  ${GREEN}sync${NC}              Sync environment with requirements.txt (recommended)"
        echo "  ${GREEN}freeze${NC}            Generate requirements.txt from current environment"
        echo "  ${GREEN}list${NC}              List all installed packages"
        echo "  ${GREEN}show <pkg>${NC}        Show package details"
        echo "  ${GREEN}search <term>${NC}     Search installed packages"
        echo "  ${GREEN}verify${NC}            Verify UV installation and environment"
        echo "  ${GREEN}benchmark${NC}         Compare UV vs pip speed"
        echo "  ${GREEN}clean${NC}             Clean UV cache"
        echo "  ${GREEN}help${NC}              Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 install fastapi==0.110.1"
        echo "  $0 sync                           # Sync from requirements.txt"
        echo "  $0 list | grep fastapi            # Find FastAPI"
        echo "  $0 show openai                    # Show OpenAI package info"
        echo "  $0 freeze                         # Update requirements.txt"
        echo ""
        echo "After installing/upgrading packages:"
        echo "  1. Run: $0 freeze                 # Update requirements.txt"
        echo "  2. Run: sudo supervisorctl restart backend"
        echo ""
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
