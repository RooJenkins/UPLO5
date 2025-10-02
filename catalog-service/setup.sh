#!/bin/bash

# UPLO-DB Complete Setup Script
# Automates local development environment setup

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

clear

echo -e "${PURPLE}"
echo "╔════════════════════════════════════════╗"
echo "║     UPLO-DB Setup Script v1.0          ║"
echo "║   Automated Development Environment    ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Step 1: Check Python
echo -e "${BLUE}[1/6]${NC} Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Install Python 3.10+ from: https://www.python.org"
    exit 1
fi
echo ""

# Step 2: Create virtual environment
echo -e "${BLUE}[2/6]${NC} Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi
echo ""

# Step 3: Activate and install dependencies
echo -e "${BLUE}[3/6]${NC} Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 4: Install Playwright
echo -e "${BLUE}[4/6]${NC} Installing Playwright browsers..."
playwright install chromium --quiet
echo -e "${GREEN}✅ Playwright browser installed${NC}"
echo ""

# Step 5: Check database connection
echo -e "${BLUE}[5/6]${NC} Checking database configuration..."
if [ -z "$DATABASE_URL" ]; then
    echo -e "${YELLOW}⚠️  DATABASE_URL not set${NC}"
    echo ""
    echo "To connect to a database, set DATABASE_URL:"
    echo "  export DATABASE_URL='postgresql://user:pass@host:5432/dbname'"
    echo ""
    echo "Or create a .env file:"
    echo "  DATABASE_URL=postgresql://user:pass@host:5432/dbname"
    echo ""
    echo -e "${YELLOW}Skipping database check${NC}"
else
    echo -e "${GREEN}✅ DATABASE_URL configured${NC}"
    echo ""
    echo -n "Testing connection... "
    if psql "$DATABASE_URL" -c "SELECT 1" &> /dev/null; then
        echo -e "${GREEN}✅ Connection successful${NC}"
    else
        echo -e "${RED}❌ Connection failed${NC}"
        echo "Check your DATABASE_URL"
    fi
fi
echo ""

# Step 6: Summary
echo -e "${BLUE}[6/6]${NC} Setup complete!"
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Setup Complete! 🎉                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. Set up database (if not done):"
echo "   ${YELLOW}export DATABASE_URL='your-postgresql-url'${NC}"
echo "   ${YELLOW}psql \$DATABASE_URL < backend/database/schema.sql${NC}"
echo ""
echo "2. Run the scraper:"
echo "   ${YELLOW}python scraper/run.py --source asos --limit 50${NC}"
echo ""
echo "3. Start the API server:"
echo "   ${YELLOW}uvicorn backend.api.main:app --reload${NC}"
echo ""
echo "4. Test the API:"
echo "   ${YELLOW}./test-api.sh http://localhost:8000${NC}"
echo ""
echo "5. Deploy to Railway:"
echo "   ${YELLOW}./deploy.sh${NC}"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
