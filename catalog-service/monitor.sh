#!/bin/bash

# UPLO-DB Production Monitoring Script
# Check API health and catalog status

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# API URL from argument or environment
API_URL="${1:-${UPLO_DB_API_URL:-http://localhost:8000}}"

echo "🔍 UPLO-DB Monitoring Dashboard"
echo "================================"
echo "API: $API_URL"
echo ""

# Function to make API calls
api_call() {
    local endpoint="$1"
    curl -s -w "\n%{http_code}" "$API_URL$endpoint" 2>/dev/null
}

# Parse response
parse_response() {
    local response="$1"
    local body=$(echo "$response" | head -n -1)
    local status=$(echo "$response" | tail -n 1)

    echo "$body"
    return $status
}

# Test health endpoint
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Health Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

health_response=$(api_call "/api/v1/health")
health_body=$(echo "$health_response" | head -n -1)
health_status=$(echo "$health_response" | tail -n 1)

if [ "$health_status" = "200" ]; then
    echo -e "${GREEN}✅ API is healthy${NC}"

    # Parse health data
    if command -v jq &> /dev/null; then
        catalog_size=$(echo "$health_body" | jq -r '.catalog_size // 0')
        last_scrape=$(echo "$health_body" | jq -r '.last_scrape // "never"')

        echo ""
        echo "  📊 Catalog Size: $catalog_size products"
        echo "  🕐 Last Scrape: $last_scrape"
    fi
else
    echo -e "${RED}❌ API is unhealthy (HTTP $health_status)${NC}"
fi

echo ""

# Test stats endpoint
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Catalog Statistics${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

stats_response=$(api_call "/api/v1/stats")
stats_body=$(echo "$stats_response" | head -n -1)
stats_status=$(echo "$stats_response" | tail -n 1)

if [ "$stats_status" = "200" ]; then
    echo -e "${GREEN}✅ Stats retrieved${NC}"

    if command -v jq &> /dev/null; then
        echo ""
        echo "$stats_body" | jq -r '
            "  Total Products: \(.total_products // 0)\n" +
            "  Total Brands: \(.total_brands // 0)\n" +
            "\n  Products by Brand:"
        '

        echo "$stats_body" | jq -r '.by_brand | to_entries[] | "    • \(.key): \(.value)"' 2>/dev/null || true
    fi
else
    echo -e "${YELLOW}⚠️  Could not retrieve stats${NC}"
fi

echo ""

# Test feed endpoint
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Feed Performance${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

start=$(date +%s%3N)
feed_response=$(api_call "/api/v1/feed?limit=20")
end=$(date +%s%3N)
duration=$((end - start))

feed_status=$(echo "$feed_response" | tail -n 1)

if [ "$feed_status" = "200" ]; then
    if [ $duration -lt 150 ]; then
        echo -e "${GREEN}✅ Feed response: ${duration}ms (EXCELLENT)${NC}"
    elif [ $duration -lt 300 ]; then
        echo -e "${YELLOW}⚠️  Feed response: ${duration}ms (ACCEPTABLE)${NC}"
    else
        echo -e "${RED}❌ Feed response: ${duration}ms (TOO SLOW)${NC}"
    fi
else
    echo -e "${RED}❌ Feed endpoint failed${NC}"
fi

echo ""

# Alert conditions
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Alert Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

ALERTS=0

# Check if API is down
if [ "$health_status" != "200" ]; then
    echo -e "${RED}🚨 CRITICAL: API is down or unreachable${NC}"
    ALERTS=$((ALERTS + 1))
fi

# Check if catalog is empty
if command -v jq &> /dev/null; then
    catalog_size=$(echo "$health_body" | jq -r '.catalog_size // 0' 2>/dev/null)
    if [ "$catalog_size" -eq 0 ] 2>/dev/null; then
        echo -e "${YELLOW}⚠️  WARNING: Catalog is empty - run scraper${NC}"
        ALERTS=$((ALERTS + 1))
    fi
fi

# Check response time
if [ $duration -gt 500 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Slow response times (${duration}ms)${NC}"
    ALERTS=$((ALERTS + 1))
fi

if [ $ALERTS -eq 0 ]; then
    echo -e "${GREEN}✅ No alerts - system is healthy${NC}"
fi

echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ "$health_status" = "200" ] && [ $duration -lt 300 ] && [ "$catalog_size" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}🎉 System Status: HEALTHY${NC}"
    echo ""
    echo "Everything is working properly!"
    exit 0
elif [ "$health_status" = "200" ]; then
    echo -e "${YELLOW}⚠️  System Status: DEGRADED${NC}"
    echo ""
    echo "API is up but there are warnings."
    exit 0
else
    echo -e "${RED}❌ System Status: CRITICAL${NC}"
    echo ""
    echo "API is not responding properly!"
    exit 1
fi
