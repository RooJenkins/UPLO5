#!/bin/bash

# UPLO-DB Catalog Service - Quick Deploy Script
# Makes deployment to Railway super easy!

set -e  # Exit on error

echo "🚀 UPLO-DB Catalog Service - Railway Deployment"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found${NC}"
    echo ""
    echo "Install it with:"
    echo "  npm install -g @railway/cli"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Railway CLI found${NC}"
echo ""

# Check if already logged in
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Railway${NC}"
    echo ""
    echo "Logging in..."
    railway login
    echo ""
fi

echo -e "${GREEN}✅ Logged in to Railway${NC}"
echo ""

# Check if project exists
if ! railway status &> /dev/null; then
    echo -e "${YELLOW}⚠️  No Railway project found${NC}"
    echo ""
    echo "Creating new project..."
    railway init
    echo ""
fi

echo -e "${GREEN}✅ Railway project ready${NC}"
echo ""

# Check environment variables
echo -e "${BLUE}📋 Checking environment variables...${NC}"
echo ""

if ! railway variables get DATABASE_URL &> /dev/null; then
    echo -e "${RED}❌ DATABASE_URL not set${NC}"
    echo ""
    echo "Set it with:"
    echo "  railway variables set DATABASE_URL='your-postgresql-url'"
    echo ""
    echo "Or set it in Railway dashboard: https://railway.app/dashboard"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ DATABASE_URL configured${NC}"
echo ""

# Deploy
echo -e "${BLUE}🚀 Deploying to Railway...${NC}"
echo ""

railway up

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

# Get the URL
echo -e "${BLUE}📍 Getting your API URL...${NC}"
echo ""

DOMAIN=$(railway domain 2>/dev/null || echo "not-set")

if [ "$DOMAIN" != "not-set" ]; then
    echo -e "${GREEN}✅ Your API is live at:${NC}"
    echo "   https://$DOMAIN"
    echo ""
    echo "Test it:"
    echo "   curl https://$DOMAIN/api/v1/health"
    echo ""
else
    echo -e "${YELLOW}⚠️  No domain set yet${NC}"
    echo ""
    echo "Generate one with:"
    echo "  railway domain"
    echo ""
fi

echo ""
echo -e "${GREEN}🎉 Next steps:${NC}"
echo ""
echo "1. Test API health:"
echo "   curl https://$DOMAIN/api/v1/health"
echo ""
echo "2. Update your .env file:"
echo "   EXPO_PUBLIC_UPLO_DB_API_URL=https://$DOMAIN/api/v1"
echo ""
echo "3. Run the scraper:"
echo "   python scraper/run.py --source asos --limit 500"
echo ""
echo "4. View logs:"
echo "   railway logs"
echo ""
echo -e "${GREEN}Done! 🚀${NC}"
