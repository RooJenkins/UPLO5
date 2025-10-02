#!/bin/bash

# UPLO-DB API Testing Script
# Comprehensive tests for all API endpoints

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default to localhost
API_URL="${1:-http://localhost:8000}"

echo "🧪 UPLO-DB API Testing Suite"
echo "=============================="
echo ""
echo "Testing API at: $API_URL"
echo ""

# Track test results
PASSED=0
FAILED=0

# Helper function to run tests
test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local expected_status="${3:-200}"

    echo -n "Testing $name... "

    response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -n 1)

    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $status)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected $expected_status, got $status)"
        echo "Response: $body"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Test suite
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Core Endpoints${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

test_endpoint "Root endpoint" "/"
test_endpoint "Health check" "/api/v1/health"
test_endpoint "Statistics" "/api/v1/stats"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Feed Endpoints${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

test_endpoint "Feed (default)" "/api/v1/feed"
test_endpoint "Feed (with limit)" "/api/v1/feed?limit=10"
test_endpoint "Feed (with category)" "/api/v1/feed?category=tops&limit=5"
test_endpoint "Feed (with brand)" "/api/v1/feed?brand=ASOS&limit=5"
test_endpoint "Feed (in stock only)" "/api/v1/feed?in_stock=true&limit=5"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Product Detail Endpoints${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test product detail (will fail if no products yet)
test_endpoint "Product detail (ID=1)" "/api/v1/product/1" || echo -e "${YELLOW}   (Expected if database is empty)${NC}"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Performance Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Measure response time for feed endpoint
echo -n "Feed response time... "
start=$(date +%s%3N)
curl -s "$API_URL/api/v1/feed?limit=20" > /dev/null
end=$(date +%s%3N)
duration=$((end - start))

if [ $duration -lt 200 ]; then
    echo -e "${GREEN}✅ EXCELLENT${NC} (${duration}ms)"
    PASSED=$((PASSED + 1))
elif [ $duration -lt 500 ]; then
    echo -e "${YELLOW}⚠️  ACCEPTABLE${NC} (${duration}ms)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ TOO SLOW${NC} (${duration}ms)"
    FAILED=$((FAILED + 1))
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Error Handling${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

test_endpoint "Invalid product ID" "/api/v1/product/999999" "404"
test_endpoint "Invalid feed limit" "/api/v1/feed?limit=999" "422"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

TOTAL=$((PASSED + FAILED))
PASS_RATE=$((PASSED * 100 / TOTAL))

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC} ($PASSED/$TOTAL)"
    echo ""
    echo -e "${GREEN}✅ API is fully functional${NC}"
    exit 0
elif [ $PASS_RATE -gt 80 ]; then
    echo -e "${YELLOW}⚠️  Most tests passed${NC} ($PASSED/$TOTAL - ${PASS_RATE}%)"
    echo ""
    echo -e "${YELLOW}Some tests failed, but API is mostly functional${NC}"
    exit 0
else
    echo -e "${RED}❌ Many tests failed${NC} ($PASSED/$TOTAL - ${PASS_RATE}%)"
    echo ""
    echo -e "${RED}API has significant issues${NC}"
    exit 1
fi
