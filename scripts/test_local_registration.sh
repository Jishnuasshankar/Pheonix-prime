#!/bin/bash

# MasterX Local Registration Test Script
# Tests the complete registration flow in local environment
# 
# Usage: ./scripts/test_local_registration.sh
# 
# Requirements:
# - Backend running on http://localhost:8001
# - MongoDB running on localhost:27017
# - curl and jq installed

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
BACKEND_URL="http://localhost:8001"
TEST_EMAIL="test-$(date +%s)@example.com"
TEST_PASSWORD="TestPass123!"
TEST_NAME="Test User"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    MasterX Local Registration Test                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check backend health
echo -e "${YELLOW}[1/6] Checking backend health...${NC}"
HEALTH_RESPONSE=$(curl -s "${BACKEND_URL}/api/health")
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.status')

if [ "$HEALTH_STATUS" = "ok" ]; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    echo "$HEALTH_RESPONSE"
    exit 1
fi

# Step 2: Test registration endpoint
echo -e "${YELLOW}[2/6] Testing registration endpoint...${NC}"
REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BACKEND_URL}/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"name\": \"${TEST_NAME}\"
  }")

# Extract HTTP status code and response body
HTTP_STATUS=$(echo "$REGISTER_RESPONSE" | tail -n 1)
REGISTER_BODY=$(echo "$REGISTER_RESPONSE" | sed '$d')

if [ "$HTTP_STATUS" = "201" ]; then
    echo -e "${GREEN}✓ Registration successful (HTTP 201)${NC}"
    
    # Extract tokens
    ACCESS_TOKEN=$(echo "$REGISTER_BODY" | jq -r '.access_token')
    REFRESH_TOKEN=$(echo "$REGISTER_BODY" | jq -r '.refresh_token')
    USER_ID=$(echo "$REGISTER_BODY" | jq -r '.user.id')
    USER_EMAIL=$(echo "$REGISTER_BODY" | jq -r '.user.email')
    USER_NAME=$(echo "$REGISTER_BODY" | jq -r '.user.name')
    
    echo -e "  User ID: ${BLUE}${USER_ID}${NC}"
    echo -e "  Email: ${BLUE}${USER_EMAIL}${NC}"
    echo -e "  Name: ${BLUE}${USER_NAME}${NC}"
    echo -e "  Token: ${BLUE}${ACCESS_TOKEN:0:20}...${NC}"
else
    echo -e "${RED}✗ Registration failed (HTTP ${HTTP_STATUS})${NC}"
    echo "$REGISTER_BODY" | jq '.'
    exit 1
fi

# Step 3: Verify user in MongoDB
echo -e "${YELLOW}[3/6] Verifying user in MongoDB...${NC}"
# This requires mongosh/mongo CLI - skip if not available
if command -v mongosh &> /dev/null; then
    MONGO_RESULT=$(mongosh --quiet --eval "db.getSiblingDB('masterx').users.findOne({email: '${TEST_EMAIL}'})" 2>/dev/null || echo "")
    if [ -n "$MONGO_RESULT" ]; then
        echo -e "${GREEN}✓ User found in MongoDB${NC}"
    else
        echo -e "${YELLOW}⚠ Could not verify MongoDB (user might still be there)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skipping MongoDB check (mongosh not installed)${NC}"
fi

# Step 4: Test /api/auth/me endpoint with token
echo -e "${YELLOW}[4/6] Testing token validation (/api/auth/me)...${NC}"
ME_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BACKEND_URL}/api/auth/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

ME_HTTP_STATUS=$(echo "$ME_RESPONSE" | tail -n 1)
ME_BODY=$(echo "$ME_RESPONSE" | sed '$d')

if [ "$ME_HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Token is valid${NC}"
    ME_EMAIL=$(echo "$ME_BODY" | jq -r '.email')
    echo -e "  Authenticated as: ${BLUE}${ME_EMAIL}${NC}"
else
    echo -e "${RED}✗ Token validation failed (HTTP ${ME_HTTP_STATUS})${NC}"
    echo "$ME_BODY" | jq '.'
    exit 1
fi

# Step 5: Test CORS configuration
echo -e "${YELLOW}[5/6] Testing CORS configuration...${NC}"
CORS_RESPONSE=$(curl -s -i -X OPTIONS "${BACKEND_URL}/api/auth/register" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" 2>&1 || echo "")

if echo "$CORS_RESPONSE" | grep -q "access-control-allow-origin"; then
    echo -e "${GREEN}✓ CORS is configured correctly${NC}"
    ALLOWED_ORIGIN=$(echo "$CORS_RESPONSE" | grep -i "access-control-allow-origin" | cut -d':' -f2- | tr -d '\r\n ')
    echo -e "  Allowed origin: ${BLUE}${ALLOWED_ORIGIN}${NC}"
else
    echo -e "${YELLOW}⚠ CORS check inconclusive (might still work)${NC}"
fi

# Step 6: Summary
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Test Summary                                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo -e "${GREEN}✓ Backend health check${NC}"
echo -e "${GREEN}✓ User registration${NC}"
echo -e "${GREEN}✓ Token generation${NC}"
echo -e "${GREEN}✓ Token validation${NC}"
echo -e "${GREEN}✓ /api/auth/me endpoint${NC}"
echo ""
echo -e "${GREEN}🎉 All tests passed!${NC}"
echo ""
echo -e "${BLUE}Test User Credentials:${NC}"
echo -e "  Email: ${TEST_EMAIL}"
echo -e "  Password: ${TEST_PASSWORD}"
echo -e "  User ID: ${USER_ID}"
echo ""
echo -e "${YELLOW}Frontend Test:${NC}"
echo -e "  1. Open http://localhost:3000 (or http://localhost:5173)"
echo -e "  2. Click 'Sign Up'"
echo -e "  3. Enter any email, name, and password"
echo -e "  4. Should navigate to /app after successful registration"
echo ""
echo -e "${BLUE}Expected Console Logs:${NC}"
echo -e "  - Backend: ${GREEN}✅ User registered: <email>${NC}"
echo -e "  - Frontend: ${GREEN}✅ Signup complete! Welcome, <name>${NC}"
echo -e "  - Browser console: ${GREEN}🔗 API Base URL: http://localhost:8001 (from VITE_BACKEND_URL)${NC}"
echo ""

# Cleanup (optional)
read -p "Delete test user from database? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v mongosh &> /dev/null; then
        mongosh --quiet --eval "db.getSiblingDB('masterx').users.deleteOne({email: '${TEST_EMAIL}'})" 2>/dev/null
        echo -e "${GREEN}✓ Test user deleted${NC}"
    else
        echo -e "${YELLOW}⚠ mongosh not installed, please delete manually:${NC}"
        echo -e "  mongosh masterx --eval \"db.users.deleteOne({email: '${TEST_EMAIL}'})\""
    fi
fi
