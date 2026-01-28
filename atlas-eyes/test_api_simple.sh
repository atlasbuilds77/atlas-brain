#!/bin/bash

# Simple API Test Script using curl
# No Python dependencies needed

API_URL="http://localhost:5001"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}Atlas Eyes API Simple Test${NC}"
echo -e "${CYAN}================================${NC}\n"

PASS=0
FAIL=0

test_endpoint() {
    local name=$1
    local endpoint=$2
    
    echo -e "${CYAN}Testing: $name${NC}"
    response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint" 2>&1)
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ PASS${NC} - Status: $http_code"
        echo "$body" | python3 -m json.tool 2>/dev/null | head -10
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌ FAIL${NC} - Status: $http_code"
        echo "$body"
        FAIL=$((FAIL + 1))
    fi
    echo
}

# Test endpoints
test_endpoint "GET /api/status" "/api/status"
test_endpoint "GET /api/heartbeat" "/api/heartbeat"
test_endpoint "GET /api/tremor" "/api/tremor"
test_endpoint "GET /api/roi" "/api/roi"
test_endpoint "GET /api/motion" "/api/motion"
test_endpoint "GET /api/frequency" "/api/frequency"

# Summary
echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo -e "${CYAN}================================${NC}\n"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}\n"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed${NC}\n"
    exit 1
fi
