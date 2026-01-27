#!/bin/bash
# =====================================================
# KRONOS SMOKE TEST SCRIPT
# =====================================================
# Usage: ./smoke-test.sh [base_url]
# Example: ./smoke-test.sh https://app.kronos.app
# =====================================================

set -euo pipefail

BASE_URL=${1:-http://localhost:8000}
FAILED=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "Kronos Smoke Tests"
echo "========================================="
echo "Target: $BASE_URL"
echo ""

# Test function
test_endpoint() {
    local name=$1
    local endpoint=$2
    local expected_status=${3:-200}
    
    printf "Testing %-30s " "$name..."
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" || echo "000")
    
    if [ "$status" == "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $status)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Health checks
echo -e "\n${YELLOW}Health Endpoints${NC}"
test_endpoint "API Health" "/health"
test_endpoint "API Ready" "/ready"

# API endpoints
echo -e "\n${YELLOW}API Endpoints${NC}"
test_endpoint "API Root" "/api/v1"
test_endpoint "API Docs" "/docs"
test_endpoint "OpenAPI Schema" "/openapi.json"

# Auth endpoints (should return 401 without token)
echo -e "\n${YELLOW}Auth Endpoints${NC}"
test_endpoint "Auth Required" "/api/v1/users/me" "401"

# Public endpoints
echo -e "\n${YELLOW}Public Endpoints${NC}"
test_endpoint "Lead Form Config" "/api/v1/public/lead-form"

# Response time check
echo -e "\n${YELLOW}Performance Check${NC}"
printf "Testing %-30s " "Response time..."
response_time=$(curl -s -o /dev/null -w "%{time_total}" "$BASE_URL/health")
response_ms=$(echo "$response_time * 1000" | bc | cut -d. -f1)

if [ "$response_ms" -lt 500 ]; then
    echo -e "${GREEN}✓ PASS${NC} (${response_ms}ms)"
else
    echo -e "${YELLOW}⚠ SLOW${NC} (${response_ms}ms)"
fi

# Summary
echo ""
echo "========================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All smoke tests passed!${NC}"
    exit 0
else
    echo -e "${RED}$FAILED test(s) failed${NC}"
    exit 1
fi
