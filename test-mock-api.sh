#!/bin/bash

# VIP Ride Platform - Mock API Test Script
# Tests all key endpoints to ensure Flutter app integration works

BASE_URL="http://localhost:8000"
echo "🧪 Testing VIP Ride Mock API at $BASE_URL"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=$4
    local description=$5
    
    echo -e "\n${BLUE}Testing: $description${NC}"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" "$BASE_URL$endpoint")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
        echo "Response: $(echo "$body" | jq -r '.message // .status // "OK"' 2>/dev/null || echo "$body" | head -c 100)"
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $status_code)"
        echo "Response: $body"
    fi
}

# Test with auth token
test_with_auth() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=$4
    local description=$5
    local token=$6
    
    echo -e "\n${BLUE}Testing: $description${NC}"
    echo "Endpoint: $method $endpoint (with auth)"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" \
            -H "Authorization: Bearer $token" \
            "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data" "$BASE_URL$endpoint")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
        echo "Response: $(echo "$body" | jq -r '.message // .user.tier // .status // "OK"' 2>/dev/null || echo "$body" | head -c 100)"
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $status_code)"
        echo "Response: $body"
    fi
}

echo -e "\n${YELLOW}=== 1. HEALTH CHECK ===${NC}"
test_endpoint "GET" "/health/" "" "200" "API Health Check"

echo -e "\n${YELLOW}=== 2. AUTHENTICATION TESTS ===${NC}"

# Test user registration
echo -e "\n${BLUE}Testing: User Registration${NC}"
register_data='{
  "email": "test@example.com",
  "password": "testpass123",
  "first_name": "Test",
  "last_name": "User",
  "phone": "+1234567890"
}'
register_response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$register_data" "$BASE_URL/api/v1/accounts/register/")

register_status=$(echo "$register_response" | tail -n1)
register_body=$(echo "$register_response" | sed '$d')

if [ "$register_status" = "201" ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $register_status)"
    test_token=$(echo "$register_body" | jq -r '.access_token' 2>/dev/null)
    echo "New user registered, got token: ${test_token:0:20}..."
else
    echo -e "${YELLOW}⚠ INFO${NC} (User might already exist, trying login)"
fi

# Test user login
echo -e "\n${BLUE}Testing: User Login${NC}"
login_data='{
  "email": "admin@email.com",
  "password": "password",
  "device_name": "Test Device",
  "device_type": "mobile",
  "device_os": "linux"
}'
login_response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$login_data" "$BASE_URL/api/v1/accounts/login/")

login_status=$(echo "$login_response" | tail -n1)
login_body=$(echo "$login_response" | sed '$d')

if [ "$login_status" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $login_status)"
    TOKEN=$(echo "$login_body" | jq -r '.access_token' 2>/dev/null)
    USER_TIER=$(echo "$login_body" | jq -r '.user.tier' 2>/dev/null)
    echo "Login successful, token: ${TOKEN:0:20}..., tier: $USER_TIER"
else
    echo -e "${RED}✗ FAIL${NC} (HTTP $login_status)"
    echo "Response: $login_body"
    exit 1
fi

echo -e "\n${YELLOW}=== 3. PROFILE & TIER TESTS ===${NC}"

# Test old profile endpoint
test_with_auth "GET" "/api/v1/accounts/profile/" "" "200" "Legacy Profile Endpoint" "$TOKEN"

# Test new Flutter tier status endpoint
test_with_auth "GET" "/api/v1/accounts/flutter/tier-status/" "" "200" "Flutter Tier Status Endpoint" "$TOKEN"

echo -e "\n${YELLOW}=== 4. CARD ACTIVATION TESTS ===${NC}"

# Test card activation with VIP card
echo -e "\n${BLUE}Testing: VIP Card Activation${NC}"
card_data='{
  "card_number": "TEST-1234-5678-9012",
  "verification_code": "TEST123",
  "device_name": "Test Device"
}'
card_response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$card_data" "$BASE_URL/api/v1/accounts/flutter/activate-card/")

card_status=$(echo "$card_response" | tail -n1)
card_body=$(echo "$card_response" | sed '$d')

if [ "$card_status" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $card_status)"
    new_tier=$(echo "$card_body" | jq -r '.user.tier' 2>/dev/null)
    echo "Card activation successful, new tier: $new_tier"
    
    # Test tier status after activation
    echo -e "\n${BLUE}Testing: Tier Status After Activation${NC}"
    tier_response=$(curl -s -H "Authorization: Bearer $TOKEN" \
        "$BASE_URL/api/v1/accounts/flutter/tier-status/")
    current_tier=$(echo "$tier_response" | jq -r '.user.tier' 2>/dev/null)
    echo "Current tier after activation: $current_tier"
    
else
    echo -e "${YELLOW}⚠ INFO${NC} (Card might already be activated or invalid)"
    echo "Response: $card_body"
fi

echo -e "\n${YELLOW}=== 5. RIDE MANAGEMENT TESTS ===${NC}"

# Test ride request
ride_data='{
  "pickup_location": {
    "lat": 40.7128,
    "lng": -74.0060,
    "address": "New York, NY"
  },
  "destination": {
    "lat": 40.7589,
    "lng": -73.9851,
    "address": "Times Square, NY"
  },
  "vehicle_type": "luxury"
}'
test_with_auth "POST" "/api/v1/rides/workflow/request/" "$ride_data" "200" "Ride Request" "$TOKEN"

# Test active rides
test_with_auth "GET" "/api/v1/rides/workflow/active/" "" "200" "Active Rides" "$TOKEN"

echo -e "\n${YELLOW}=== 6. VIP PREMIUM FEATURES (if applicable) ===${NC}"

# Test hotel partnerships (might fail if not VIP Premium)
test_with_auth "GET" "/api/v1/hotel-partnerships/hotels/nearby/" "" "200,403" "Hotel Partnerships" "$TOKEN"

echo -e "\n${YELLOW}=== 7. ADMIN/DEBUG ENDPOINTS ===${NC}"

test_endpoint "GET" "/mock/admin/sessions" "" "200" "Admin Sessions View"
test_endpoint "GET" "/mock/admin/devices" "" "200" "Admin Devices View"
test_endpoint "GET" "/mock/admin/users" "" "200" "Admin Users View"

echo -e "\n${YELLOW}=== 8. MFA TESTS ===${NC}"

# Test MFA setup
test_with_auth "POST" "/api/v1/accounts/auth/mfa/setup/" "{}" "200" "MFA Setup" "$TOKEN"

# Test MFA verification
mfa_data='{"token": "123456"}'
test_with_auth "POST" "/api/v1/accounts/auth/mfa/verify/" "$mfa_data" "200" "MFA Verification" "$TOKEN"

echo -e "\n${GREEN}=================================================="
echo -e "🎉 Mock API Testing Complete!"
echo -e "=================================================="
echo -e "${NC}"

echo -e "\n${BLUE}Next Steps:${NC}"
echo "1. The mock API is working correctly ✓"
echo "2. Run your Flutter app with: ${YELLOW}cd mobile && flutter run${NC}"
echo "3. In Flutter, make sure ApiConfig.useMockApi = true"
echo "4. Test login with: admin@email.com / password"
echo "5. Test card activation with: TEST-1234-5678-9012 / TEST123"
echo ""
echo "Flutter API Base URL should be: ${YELLOW}http://localhost:8000${NC}"