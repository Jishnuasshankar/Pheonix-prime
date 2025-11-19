#!/bin/bash
# ==============================================================================
# MasterX - Docker Setup Verification Script
# ==============================================================================
# Tests Docker configuration and builds images
# Run this script to verify your Docker setup is correct
# ==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0

print_header() {
    echo -e "${BLUE}===============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===============================================================================${NC}"
}

print_test() {
    echo -e "${YELLOW}🔍 TEST: $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
    ((PASSED++))
}

print_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
    ((FAILED++))
}

print_info() {
    echo -e "${BLUE}ℹ️  INFO: $1${NC}"
}

# Test 1: Docker Installation
print_header "Test 1: Docker Installation"
print_test "Checking Docker Engine"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_pass "Docker installed: $DOCKER_VERSION"
else
    print_fail "Docker is not installed"
    exit 1
fi

# Test 2: Docker Compose
print_header "Test 2: Docker Compose"
print_test "Checking Docker Compose"
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_pass "Docker Compose installed: $COMPOSE_VERSION"
else
    print_fail "Docker Compose is not installed"
    exit 1
fi

# Test 3: Docker Service Running
print_header "Test 3: Docker Service Status"
print_test "Checking if Docker daemon is running"
if docker info &> /dev/null; then
    print_pass "Docker daemon is running"
else
    print_fail "Docker daemon is not running"
    exit 1
fi

# Test 4: File Structure
print_header "Test 4: Docker Files Exist"
FILES=(
    "backend/Dockerfile"
    "backend/.dockerignore"
    "frontend/Dockerfile"
    "frontend/Dockerfile.dev"
    "frontend/.dockerignore"
    "frontend/nginx.conf"
    "docker-compose.dev.yml"
    "docker-compose.prod.yml"
    ".env.docker.example"
)

for file in "${FILES[@]}"; do
    print_test "Checking $file"
    if [ -f "$file" ]; then
        print_pass "$file exists"
    else
        print_fail "$file is missing"
    fi
done

# Test 5: Environment File
print_header "Test 5: Environment Configuration"
print_test "Checking .env file"
if [ -f ".env" ]; then
    print_pass ".env file exists"
    
    # Check required variables
    REQUIRED_VARS=(
        "MONGO_ROOT_PASSWORD"
        "JWT_SECRET_KEY"
        "GROQ_API_KEY"
        "GEMINI_API_KEY"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$var=" .env; then
            VALUE=$(grep "^$var=" .env | cut -d '=' -f2)
            if [ ! -z "$VALUE" ] && [ "$VALUE" != "your_*" ] && [ "$VALUE" != "CHANGE_*" ]; then
                print_pass "$var is configured"
            else
                print_fail "$var is not configured (using placeholder)"
            fi
        else
            print_fail "$var is missing from .env"
        fi
    done
else
    print_fail ".env file not found (copy from .env.docker.example)"
fi

# Test 6: Build Backend Image (Dry Run)
print_header "Test 6: Backend Dockerfile Syntax"
print_test "Validating backend Dockerfile"
if docker build -f backend/Dockerfile backend/ --target builder -t masterx-backend-test:latest > /dev/null 2>&1; then
    print_pass "Backend Dockerfile syntax is valid"
    docker rmi masterx-backend-test:latest > /dev/null 2>&1 || true
else
    print_fail "Backend Dockerfile has syntax errors"
fi

# Test 7: Build Frontend Image (Dry Run)
print_header "Test 7: Frontend Dockerfile Syntax"
print_test "Validating frontend Dockerfile"
if docker build -f frontend/Dockerfile frontend/ --target builder -t masterx-frontend-test:latest > /dev/null 2>&1; then
    print_pass "Frontend Dockerfile syntax is valid"
    docker rmi masterx-frontend-test:latest > /dev/null 2>&1 || true
else
    print_fail "Frontend Dockerfile has syntax errors"
fi

# Test 8: Docker Compose Validation
print_header "Test 8: Docker Compose Configuration"
print_test "Validating docker-compose.dev.yml"
if docker-compose -f docker-compose.dev.yml config > /dev/null 2>&1; then
    print_pass "docker-compose.dev.yml is valid"
else
    print_fail "docker-compose.dev.yml has errors"
fi

print_test "Validating docker-compose.prod.yml"
if docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
    print_pass "docker-compose.prod.yml is valid"
else
    print_fail "docker-compose.prod.yml has errors"
fi

# Test 9: Network Configuration
print_header "Test 9: Port Availability"
PORTS=(3000 8001 27017)
for port in "${PORTS[@]}"; do
    print_test "Checking if port $port is available"
    if ! lsof -Pi :$port -sTCP:LISTEN -t > /dev/null 2>&1; then
        print_pass "Port $port is available"
    else
        print_fail "Port $port is already in use"
    fi
done

# Test 10: System Resources
print_header "Test 10: System Resources"
print_test "Checking available disk space"
AVAILABLE_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE_GB" -gt 20 ]; then
    print_pass "Sufficient disk space: ${AVAILABLE_GB}GB available"
else
    print_fail "Insufficient disk space: ${AVAILABLE_GB}GB (need 20GB+)"
fi

print_test "Checking available memory"
AVAILABLE_MB=$(free -m | grep Mem: | awk '{print $7}')
if [ "$AVAILABLE_MB" -gt 4000 ]; then
    print_pass "Sufficient memory: ${AVAILABLE_MB}MB available"
else
    print_fail "Insufficient memory: ${AVAILABLE_MB}MB (need 4GB+)"
fi

# Summary
print_header "Test Summary"
TOTAL=$((PASSED + FAILED))
echo ""
echo "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    print_pass "All tests passed! Docker setup is ready."
    echo ""
    print_info "Next steps:"
    echo "  1. Review and update .env with your API keys"
    echo "  2. Run: ./docker-dev.sh start"
    echo "  3. Access: http://localhost:3000"
    exit 0
else
    print_fail "Some tests failed. Please fix the issues above."
    exit 1
fi
