#!/bin/bash
# MasterX Local Development - Comprehensive Signup Test
# Tests the complete signup flow to identify any disconnection points

set -e

echo "======================================"
echo "MasterX LOCAL SIGNUP TEST"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
BACKEND_URL="http://localhost:8001"
FRONTEND_URL="http://localhost:3000"
TEST_EMAIL="testlocal$(date +%s)@example.com"
TEST_PASSWORD="TestPass123!"
TEST_NAME="Local Test User"

echo "Test Configuration:"
echo "  Backend URL: $BACKEND_URL"
echo "  Frontend URL: $FRONTEND_URL"
echo "  Test Email: $TEST_EMAIL"
echo ""

# Step 1: Check backend is running
echo "Step 1: Checking backend health..."
HEALTH=$(curl -s "$BACKEND_URL/api/health" || echo "FAILED")
if [[ $HEALTH == *"ok"* ]]; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is NOT running or unreachable${NC}"
    exit 1
fi
echo ""

# Step 2: Check CORS configuration
echo "Step 2: Checking CORS configuration..."
CORS_ORIGINS=$(grep "^CORS_ORIGINS=" /app/backend/.env | cut -d'=' -f2)
echo "  CORS_ORIGINS: $CORS_ORIGINS"
if [[ $CORS_ORIGINS == *"localhost:3000"* ]] || [[ $CORS_ORIGINS == *"*"* ]]; then
    echo -e "${GREEN}✓ CORS allows localhost:3000${NC}"
else
    echo -e "${RED}✗ CORS does NOT allow localhost:3000${NC}"
    echo "  Fix: Add http://localhost:3000 to CORS_ORIGINS in /app/backend/.env"
    exit 1
fi
echo ""

# Step 3: Test registration endpoint
echo "Step 3: Testing POST /api/auth/register..."
REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"name\": \"$TEST_NAME\"
  }")

HTTP_CODE=$(echo "$REGISTER_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$REGISTER_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" == "201" ]; then
    echo -e "${GREEN}✓ Registration successful (HTTP $HTTP_CODE)${NC}"
    
    # Extract tokens
    ACCESS_TOKEN=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
    REFRESH_TOKEN=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['refresh_token'])" 2>/dev/null || echo "")
    USER_ID=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['id'])" 2>/dev/null || echo "")
    USER_EMAIL=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['email'])" 2>/dev/null || echo "")
    USER_NAME=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['name'])" 2>/dev/null || echo "")
    
    if [ -n "$ACCESS_TOKEN" ] && [ -n "$REFRESH_TOKEN" ]; then
        echo "  Access Token: ${ACCESS_TOKEN:0:50}..."
        echo "  Refresh Token: ${REFRESH_TOKEN:0:50}..."
        echo "  User ID: $USER_ID"
        echo "  User Email: $USER_EMAIL"
        echo "  User Name: $USER_NAME"
    else
        echo -e "${RED}✗ Response missing tokens or user data${NC}"
        echo "  Response: $RESPONSE_BODY"
        exit 1
    fi
else
    echo -e "${RED}✗ Registration failed (HTTP $HTTP_CODE)${NC}"
    echo "  Response: $RESPONSE_BODY"
    exit 1
fi
echo ""

# Step 4: Verify user in MongoDB
echo "Step 4: Verifying user in MongoDB..."
USER_IN_DB=$(mongosh masterx --quiet --eval "db.users.findOne({email: '$TEST_EMAIL'})" 2>/dev/null | grep -o '"email"')
if [ -n "$USER_IN_DB" ]; then
    echo -e "${GREEN}✓ User found in MongoDB${NC}"
    
    # Get user details
    IS_VERIFIED=$(mongosh masterx --quiet --eval "db.users.findOne({email: '$TEST_EMAIL'}).is_verified" 2>/dev/null)
    IS_ACTIVE=$(mongosh masterx --quiet --eval "db.users.findOne({email: '$TEST_EMAIL'}).is_active" 2>/dev/null)
    
    echo "  is_verified: $IS_VERIFIED"
    echo "  is_active: $IS_ACTIVE"
else
    echo -e "${RED}✗ User NOT found in MongoDB${NC}"
    exit 1
fi
echo ""

# Step 5: Test /api/auth/me endpoint with token
echo "Step 5: Testing GET /api/auth/me with token..."
ME_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BACKEND_URL/api/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Origin: http://localhost:3000")

ME_HTTP_CODE=$(echo "$ME_RESPONSE" | tail -n1)
ME_BODY=$(echo "$ME_RESPONSE" | head -n-1)

if [ "$ME_HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ /api/auth/me successful (HTTP $ME_HTTP_CODE)${NC}"
    
    ME_USER_ID=$(echo "$ME_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
    ME_USER_EMAIL=$(echo "$ME_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['email'])" 2>/dev/null || echo "")
    ME_USER_NAME=$(echo "$ME_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])" 2>/dev/null || echo "")
    
    echo "  User ID: $ME_USER_ID"
    echo "  User Email: $ME_USER_EMAIL"
    echo "  User Name: $ME_USER_NAME"
    
    if [ "$ME_USER_ID" == "$USER_ID" ]; then
        echo -e "${GREEN}✓ User IDs match${NC}"
    else
        echo -e "${RED}✗ User IDs don't match!${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ /api/auth/me failed (HTTP $ME_HTTP_CODE)${NC}"
    echo "  Response: $ME_BODY"
    exit 1
fi
echo ""

# Step 6: Check CORS headers in response
echo "Step 6: Checking CORS headers..."
CORS_HEADERS=$(curl -s -I -X OPTIONS "$BACKEND_URL/api/auth/register" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  2>/dev/null | grep -i "access-control")

if [ -n "$CORS_HEADERS" ]; then
    echo -e "${GREEN}✓ CORS headers present${NC}"
    echo "$CORS_HEADERS" | sed 's/^/  /'
else
    echo -e "${YELLOW}⚠ No CORS headers in OPTIONS response (may be OK if handled by middleware)${NC}"
fi
echo ""

# Step 7: Check frontend environment
echo "Step 7: Checking frontend environment..."
VITE_BACKEND_URL=$(grep "^VITE_BACKEND_URL=" /app/frontend/.env | cut -d'=' -f2)
echo "  VITE_BACKEND_URL: $VITE_BACKEND_URL"

if [ "$VITE_BACKEND_URL" == "http://localhost:8001" ]; then
    echo -e "${GREEN}✓ Frontend configured for local backend${NC}"
elif [ -z "$VITE_BACKEND_URL" ]; then
    echo -e "${YELLOW}⚠ VITE_BACKEND_URL not set (will use auto-detection)${NC}"
else
    echo -e "${YELLOW}⚠ VITE_BACKEND_URL set to: $VITE_BACKEND_URL${NC}"
fi
echo ""

# Step 8: Check frontend is running
echo "Step 8: Checking frontend..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")

if [ "$FRONTEND_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is NOT running or unreachable (HTTP $FRONTEND_RESPONSE)${NC}"
fi
echo ""

# Final summary
echo "======================================"
echo "TEST SUMMARY"
echo "======================================"
echo ""
echo -e "${GREEN}✅ All backend tests passed!${NC}"
echo ""
echo "What this means:"
echo "  1. Backend is accessible from command line"
echo "  2. Registration endpoint works correctly"
echo "  3. User is created in MongoDB"
echo "  4. JWT tokens are generated properly"
echo "  5. /api/auth/me endpoint validates tokens"
echo "  6. CORS is configured correctly"
echo ""
echo "If frontend signup still fails, the issue is likely:"
echo "  A. Frontend JavaScript not sending correct request"
echo "  B. Browser blocking the request (check browser console)"
echo "  C. Frontend not handling response correctly"
echo ""
echo "Next steps for debugging frontend:"
echo "  1. Open browser console (F12)"
echo "  2. Go to $FRONTEND_URL"
echo "  3. Try to signup"
echo "  4. Check Network tab for failed requests"
echo "  5. Check Console tab for errors"
echo ""
echo "Test user credentials:"
echo "  Email: $TEST_EMAIL"
echo "  Password: $TEST_PASSWORD"
echo ""
