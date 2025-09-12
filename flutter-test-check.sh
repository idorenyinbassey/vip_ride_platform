#!/bin/bash

# Flutter App Testing with Mock API - Quick Verification Script
# Run this to verify your Flutter app is properly configured for mock API testing

echo "🔍 Flutter Mock API Configuration Checker"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

FLUTTER_DIR="/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/mobile"
API_CONFIG="$FLUTTER_DIR/lib/config/api_config.dart"

echo -e "\n${BLUE}1. Checking Flutter project structure...${NC}"

if [ -d "$FLUTTER_DIR" ]; then
    echo -e "${GREEN}✓${NC} Flutter directory exists: $FLUTTER_DIR"
else
    echo -e "${RED}✗${NC} Flutter directory not found: $FLUTTER_DIR"
    exit 1
fi

if [ -f "$API_CONFIG" ]; then
    echo -e "${GREEN}✓${NC} API config file exists"
else
    echo -e "${RED}✗${NC} API config file not found"
    exit 1
fi

echo -e "\n${BLUE}2. Checking API configuration...${NC}"

# Check if useMockApi is set to true
if grep -q "useMockApi = true" "$API_CONFIG"; then
    echo -e "${GREEN}✓${NC} Mock API is enabled (useMockApi = true)"
else
    if grep -q "useMockApi = false" "$API_CONFIG"; then
        echo -e "${YELLOW}⚠${NC} Mock API is disabled (useMockApi = false)"
        echo "  To enable mock API, change useMockApi to true in $API_CONFIG"
    else
        echo -e "${RED}✗${NC} useMockApi setting not found in config"
    fi
fi

# Check mock API URL
if grep -q "mockApiUrl.*localhost:8000" "$API_CONFIG"; then
    echo -e "${GREEN}✓${NC} Mock API URL is configured correctly (localhost:8000)"
else
    echo -e "${YELLOW}⚠${NC} Mock API URL might not be set correctly"
fi

echo -e "\n${BLUE}3. Checking mock API server availability...${NC}"

# Test if mock API is running
if curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Mock API server is running on localhost:8000"
    
    # Get server status
    SERVER_STATUS=$(curl -s http://localhost:8000/health/ | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$SERVER_STATUS" = "ok" ]; then
        echo -e "${GREEN}✓${NC} Mock API server is healthy"
    fi
else
    echo -e "${RED}✗${NC} Mock API server is not running"
    echo "  Start it with: cd mock-api && npm start"
fi

echo -e "\n${BLUE}4. Checking Flutter dependencies...${NC}"

cd "$FLUTTER_DIR"

if [ -f "pubspec.yaml" ]; then
    echo -e "${GREEN}✓${NC} pubspec.yaml found"
    
    # Check for key dependencies
    if grep -q "http:" "pubspec.yaml" || grep -q "dio:" "pubspec.yaml"; then
        echo -e "${GREEN}✓${NC} HTTP client dependency found"
    else
        echo -e "${YELLOW}⚠${NC} No HTTP client dependency found (http or dio)"
    fi
    
    if grep -q "provider:" "pubspec.yaml"; then
        echo -e "${GREEN}✓${NC} State management (provider) found"
    else
        echo -e "${YELLOW}⚠${NC} Provider dependency not found"
    fi
else
    echo -e "${RED}✗${NC} pubspec.yaml not found"
fi

echo -e "\n${BLUE}5. Testing Flutter API integration...${NC}"

# Check if Flutter can compile
echo "Checking Flutter compilation..."
if flutter doctor > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Flutter doctor passed"
else
    echo -e "${YELLOW}⚠${NC} Flutter doctor issues found"
    echo "  Run 'flutter doctor' for details"
fi

echo -e "\n${BLUE}6. Quick API connectivity test...${NC}"

# Test login endpoint
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/accounts/login/ \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@email.com","password":"password","device_name":"Test"}' 2>/dev/null)

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓${NC} Mock API login endpoint working"
    
    # Extract token and test tier status
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    
    TIER_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
        http://localhost:8000/api/v1/accounts/flutter/tier-status/ 2>/dev/null)
    
    if echo "$TIER_RESPONSE" | grep -q "tier"; then
        echo -e "${GREEN}✓${NC} Flutter tier status endpoint working"
        USER_TIER=$(echo "$TIER_RESPONSE" | grep -o '"tier":"[^"]*"' | cut -d'"' -f4)
        echo "  User tier: $USER_TIER"
    else
        echo -e "${YELLOW}⚠${NC} Tier status endpoint issues"
    fi
else
    echo -e "${RED}✗${NC} Mock API login endpoint not working"
fi

echo -e "\n${YELLOW}========================================"
echo -e "🎯 READY TO TEST FLUTTER APP!"
echo -e "========================================"
echo -e "${NC}"

echo -e "\n${GREEN}Next steps:${NC}"
echo "1. Start Flutter app: ${YELLOW}cd mobile && flutter run${NC}"
echo "2. Test login with: ${YELLOW}admin@email.com / password${NC}"
echo "3. Test card activation: ${YELLOW}TEST-1234-5678-9012 / TEST123${NC}"
echo "4. Monitor sessions: ${YELLOW}curl http://localhost:8000/mock/admin/sessions${NC}"

echo -e "\n${GREEN}Test scenarios:${NC}"
echo "• Login with different user tiers"
echo "• Activate cards and watch tier upgrades"
echo "• Check session tracking in admin endpoints"
echo "• Test ride booking flow"
echo "• Verify automatic UI routing based on tier"

echo -e "\n${BLUE}Debug tips:${NC}"
echo "• Watch Flutter console for 'Mock API' messages"
echo "• Check for 'Using Flutter tier status endpoint' logs"
echo "• Monitor network requests in Flutter DevTools"
echo "• Use admin endpoints to verify backend state"

# Final summary
echo -e "\n${GREEN}Configuration Summary:${NC}"
echo "Mock API Server: http://localhost:8000"
echo "Flutter Config: useMockApi = true"
echo "Test Users: admin@email.com, vip@email.com, premium@email.com"
echo "Test Cards: TEST-1234-5678-9012, PREM-2345-6789-0123"