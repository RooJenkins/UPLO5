# UPLO5 System Architecture

## System Design

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    UPLO5 System                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────┐      │
│  │  Mobile App (React Native + Expo Router)    │      │
│  │                                              │      │
│  │  ┌──────────────┐  ┌──────────────┐        │      │
│  │  │  Onboarding  │  │  Feed Screen │        │      │
│  │  │  (Photo)     │  │  (Infinite)  │        │      │
│  │  └──────────────┘  └──────────────┘        │      │
│  │                                              │      │
│  │  ┌──────────────────────────────────────┐  │      │
│  │  │  FeedProvider (30-Worker System)     │  │      │
│  │  │  - Job Queue                         │  │      │
│  │  │  - Worker Pool (30 parallel)         │  │      │
│  │  │  - Image Preloader (next 5)          │  │      │
│  │  │  - Buffer Health Monitor             │  │      │
│  │  └──────────────────────────────────────┘  │      │
│  │                                              │      │
│  │  ┌──────────────────────────────────────┐  │      │
│  │  │  RorkAIClient                        │  │      │
│  │  │  - Product validation                │  │      │
│  │  │  - Image fetching & base64          │  │      │
│  │  │  - Retry logic                       │  │      │
│  │  └──────────────────────────────────────┘  │      │
│  └──────────────────┬───────────────────────┘      │
│                     │ HTTP                          │
│  ┌──────────────────┴───────────────────────┐      │
│  │  Catalog Service (FastAPI)               │      │
│  │                                           │      │
│  │  GET /api/v1/products/random             │      │
│  │  GET /api/v1/products?limit=20           │      │
│  │  GET /api/v1/health                      │      │
│  │                                           │      │
│  │  ┌─────────────────────────────────┐    │      │
│  │  │  PostgreSQL Database            │    │      │
│  │  │  - products table (2000+ rows)  │    │      │
│  │  │  - Indexes on brand, category   │    │      │
│  │  └─────────────────────────────────┘    │      │
│  └───────────────────────────────────────────      │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  Rork AI API (External)                  │      │
│  │  https://toolkit.rork.com/images/edit/   │      │
│  │  - Gemini Flash 2.5 backend              │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## Database Schema

```sql
-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    brand_name VARCHAR(200) NOT NULL,
    image_urls TEXT[] NOT NULL,
    base_price INTEGER,
    currency VARCHAR(3) DEFAULT 'USD',
    category VARCHAR(100),
    product_url VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_brand ON products(brand_name);
CREATE INDEX idx_products_category ON products(category);

-- Constraint: Ensure products have images
ALTER TABLE products ADD CONSTRAINT check_has_images
  CHECK (array_length(image_urls, 1) > 0);
```

## API Contracts

### Catalog API

**Base URL**: `http://localhost:8000/api/v1`

#### GET /products/random
Returns a random product for generation.

**Response**:
```json
{
  "id": 1,
  "product_id": 12345,
  "name": "Classic Blue Jeans",
  "brand_name": "ASOS",
  "image_urls": ["https://cdn.example.com/1.jpg"],
  "base_price": 4999,
  "currency": "USD",
  "product_url": "https://asos.com/products/12345"
}
```

#### GET /products
List products with pagination.

**Query Params**:
- `skip`: Offset (default: 0)
- `limit`: Page size (default: 20)
- `brand`: Filter by brand
- `category`: Filter by category

#### GET /health
Health check endpoint.

**Response**: `{"status": "healthy"}`

### Rork AI API

**Endpoint**: `https://toolkit.rork.com/images/edit/`

**Request**:
```json
{
  "prompt": "Professional photoshoot...",
  "images": [
    {"type": "image", "image": "<user_base64>"},
    {"type": "image", "image": "<product_base64>"}
  ]
}
```

**Response**:
```json
{
  "image": {
    "base64Data": "<generated_base64>",
    "mimeType": "image/jpeg"
  }
}
```

## Technology Stack

**Mobile**:
- React Native 0.74
- Expo SDK 51
- Expo Router 3
- TypeScript 5

**Backend**:
- FastAPI 0.110
- PostgreSQL 15
- SQLAlchemy 2.0
- Pydantic 2.0

**AI**:
- Gemini Flash 2.5 (via Rork)

## Implementation Order

1. ✅ Architecture design (this document)
2. → Catalog service (FastAPI + DB)
3. → Product scrapers (or use existing from UPLO3)
4. → Mobile app skeleton
5. → AI integration
6. → Performance optimization
7. → Testing

## Performance Targets

- 30 parallel workers
- 60fps scroll
- <3s generation time
- 80%+ buffer health
- <200MB memory usage
