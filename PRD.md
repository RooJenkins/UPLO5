# Product Requirements Document: UPLO5

**Project**: UPLO5 - AI-Powered Virtual Try-On Fashion App
**Version**: 1.0
**Date**: 2025-10-02
**Status**: Specification

---

## 1. Executive Summary

### Vision
UPLO5 is a TikTok-style mobile app that uses AI to create professional photoshoot images of users wearing real clothing from major fashion brands. Users upload one full-body photo and endlessly scroll through AI-generated images of themselves wearing different products.

### Goals
- **Personalized Fashion Discovery**: Help users visualize themselves in real products
- **Seamless UX**: Infinite scroll feed with <3s load time per item
- **High-Quality Output**: Professional white-background photoshoot quality
- **Real Products**: Integration with ASOS, H&M, Zara, Nike catalogs
- **Performance**: 60fps smooth scrolling, 30-worker parallel AI generation

### Success Metrics
- User uploads photo within 30 seconds of app launch
- 90%+ of generations complete successfully
- 60fps scroll performance maintained
- Users scroll through 20+ generated outfits per session
- <3% error rate on AI generation

---

## 2. User Stories

### Primary User: Fashion-Conscious Consumer

**As a user, I want to:**

1. **Upload My Photo**
   - Take a photo with camera OR choose from gallery
   - See immediate preview of my photo
   - Skip onboarding for quick testing (demo mode)

2. **Discover Products**
   - Scroll endlessly through AI-generated try-on images
   - See myself in real clothing from major brands
   - View product details (name, brand, price, shop link)

3. **Enjoy Smooth Performance**
   - Experience zero lag during scrolling
   - See next image instantly (preloaded)
   - Never wait for loading spinners

4. **Shop Products**
   - Tap "Shop Now" to visit product page
   - Save favorites for later
   - Share looks with friends

---

## 3. Features & Requirements

### 3.1 Core Features

#### A. User Onboarding
**Priority**: P0 (Must Have)

**Requirements:**
- Full-body photo upload via camera or gallery
- Image preview before submission
- Photo stored as base64 for AI processing
- "Skip for now" demo mode option
- Clear instructions & visual guides

**Technical Specs:**
- expo-image-picker for photo selection
- Base64 conversion for API compatibility
- Local storage persistence
- Image dimensions: Min 400x600px

#### B. AI Virtual Try-On Generation
**Priority**: P0 (Must Have)

**CRITICAL REQUIREMENTS:**
- **MUST use REAL product images** from catalog (NEVER text-only)
- **MUST fetch product image** and convert to base64
- **MUST send both** user photo + product image to Rork API
- **MUST validate** product has image_urls before generation
- **NO fallback** to text-only prompts

**Technical Specs:**
- Rork API endpoint: `https://toolkit.rork.com/images/edit/`
- Gemini Flash 2.5 backend (via Rork)
- 2-image input: user photo + product image
- Professional photoshoot prompt template
- White/neutral background output
- Full-body composition (head at 35-40% from top)

**API Request Format:**
```json
{
  "prompt": "Create professional fashion photoshoot showing person wearing exact [product] by [brand]...",
  "images": [
    { "type": "image", "image": "<user_photo_base64>" },
    { "type": "image", "image": "<product_image_base64>" }
  ]
}
```

**API Response Format:**
```json
{
  "image": {
    "base64Data": "<generated_image_base64>",
    "mimeType": "image/jpeg"
  }
}
```

#### C. Infinite Scroll Feed
**Priority**: P0 (Must Have)

**Requirements:**
- TikTok-style vertical scroll (full-screen items)
- Paging enabled (snap to each item)
- Smooth 60fps performance
- Preload next 5 items
- Dynamic loading (show more as user scrolls)

**Technical Specs:**
- React Native FlatList with paging
- `windowSize={3}` for memory efficiency
- `maxToRenderPerBatch={2}` for performance
- `getItemLayout` for instant scroll positioning
- Image.prefetch() for next 5 items

#### D. Product Catalog
**Priority**: P0 (Must Have)

**Requirements:**
- 2000+ products from major brands
- Real product data (name, brand, price, images, URL)
- Valid image URLs (verified working)
- Random product selection for variety
- Database-backed catalog

**Supported Brands:**
- ASOS (500+ products)
- H&M (500+ products)
- Zara (500+ products)
- Nike (500+ products)

**Database Schema:**
```sql
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  product_id INTEGER UNIQUE,
  name VARCHAR(500) NOT NULL,
  brand_name VARCHAR(200) NOT NULL,
  image_urls TEXT[] NOT NULL,  -- CRITICAL: Must have images
  base_price INTEGER,           -- Price in cents
  currency VARCHAR(3) DEFAULT 'USD',
  category VARCHAR(100),
  available_sizes TEXT[],
  available_colors TEXT[],
  product_url VARCHAR(1000),
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### E. 30-Worker Generation System
**Priority**: P0 (Must Have)

**Requirements:**
- 30 parallel workers (not 10!)
- Buffer health target: 80%+
- Queue-based job management
- Position locking (prevent duplicates)
- Circuit breaker for API failures

**Technical Specs:**
- Worker pool with job queue
- Concurrent API requests (max 30)
- Retry logic with exponential backoff (max 3 retries)
- Circuit breaker: OPEN after 5 consecutive failures
- Graceful degradation (try different product)

### 3.2 Secondary Features

#### F. Product Actions
**Priority**: P1 (Should Have)

- "Shop Now" button → product URL
- "Like" button → save to favorites
- "Share" button → share generated image
- Product details overlay (name, brand, price)

#### G. Feed Filters
**Priority**: P2 (Nice to Have)

- Filter by style (casual, formal, athletic)
- Filter by color
- Filter by price range
- Filter by brand

---

## 4. Technical Specifications

### 4.1 System Architecture

```
┌─────────────────────────────────────────────────┐
│              UPLO5 Architecture                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  Mobile App (React Native + Expo Router)        │
│    ├── Onboarding Screen (photo upload)        │
│    ├── Feed Screen (infinite scroll)           │
│    ├── FeedProvider (30-worker system)         │
│    └── Components (FeedCard, LoadingCard)      │
│                                                 │
│  Catalog Service (Python FastAPI)              │
│    ├── Product API (port 8000)                 │
│    ├── PostgreSQL Database                     │
│    ├── Web Scrapers (ASOS, H&M, Zara, Nike)    │
│    └── Database Migrations (Alembic)           │
│                                                 │
│  AI Service (Rork API)                          │
│    ├── Gemini Flash 2.5 (backend)              │
│    ├── Virtual Try-On Generation               │
│    └── Image Processing                        │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 4.2 Technology Stack

**Frontend:**
- React Native 0.74+
- Expo SDK 51+
- Expo Router 3+ (file-based routing)
- TypeScript 5+
- React Context (state management)

**Backend:**
- FastAPI 0.110+ (Python async framework)
- PostgreSQL 15+ (database)
- SQLAlchemy 2.0+ (ORM)
- Alembic (migrations)
- Playwright (web scraping)

**AI/ML:**
- Gemini Flash 2.5 (via Rork API)
- Image processing (base64, fetch, validate)

**Infrastructure:**
- Supabase (managed PostgreSQL)
- Vercel / Railway (FastAPI deployment)
- Expo Go (mobile testing)

### 4.3 API Endpoints

#### Catalog API

**Base URL**: `http://localhost:8000/api/v1`

**GET `/products/random`**
- **Description**: Get random product for generation
- **Response**:
```json
{
  "id": 1,
  "product_id": 12345,
  "name": "Classic Blue Jeans",
  "brand_name": "ASOS",
  "image_urls": ["https://cdn.example.com/product1.jpg", ...],
  "base_price": 4999,
  "currency": "USD",
  "product_url": "https://asos.com/products/12345"
}
```

**GET `/products`**
- **Description**: List products with pagination
- **Query Params**: `skip`, `limit`, `category`, `brand`
- **Response**: Array of products

**GET `/products/{product_id}`**
- **Description**: Get specific product
- **Response**: Single product object

**GET `/health`**
- **Description**: Health check
- **Response**: `{ "status": "healthy" }`

### 4.4 Data Flow

#### Generation Flow
```
1. User scrolls → FeedProvider detects position
2. FeedProvider checks buffer health
3. If < 80%, add jobs to queue
4. Worker picks job from queue
5. Worker fetches product from catalog API
6. Worker validates product has image_urls
7. Worker fetches product image, converts to base64
8. Worker calls Rork API with user + product images
9. Rork API returns generated image (base64)
10. Worker caches result at position
11. FeedProvider updates feed state
12. FeedCard renders generated image
```

#### Preloading Flow
```
1. User at position N
2. System preloads images at N+1, N+2, N+3, N+4, N+5
3. Image.prefetch() downloads to cache
4. User scrolls to N+1 → instant display
5. System now preloads N+6
```

### 4.5 Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| Scroll FPS | 60fps | ✅ Yes |
| Worker Count | 30 active | ✅ Yes |
| Buffer Health | 80%+ | ✅ Yes |
| Generation Time | <3s avg | ✅ Yes |
| Preload Count | Next 5 | ✅ Yes |
| Memory Usage | <200MB | ⚠️ Monitor |
| App Launch Time | <2s | ⚠️ Monitor |
| API Success Rate | 95%+ | ✅ Yes |

### 4.6 Security & Privacy

- User photos stored locally only (not uploaded to server)
- Product data public (no authentication required)
- HTTPS for all network requests
- Input validation on all API endpoints
- Rate limiting on catalog API
- SQL injection prevention (parameterized queries)

---

## 5. Success Criteria

### Must Have (P0)
- [ ] User can upload photo and see feed in <5 seconds
- [ ] Every generation uses REAL product image (never text-only)
- [ ] 60fps smooth scrolling maintained
- [ ] 30 workers active (not 10)
- [ ] 2000+ products from 4+ brands in catalog
- [ ] Professional white-background output
- [ ] Rork pays for all AI generation costs
- [ ] Product validation before every generation

### Should Have (P1)
- [ ] "Shop Now" button works
- [ ] Image preloading (next 5 items)
- [ ] 80%+ buffer health maintained
- [ ] Error handling with fallback products
- [ ] Loading states during generation

### Nice to Have (P2)
- [ ] Feed filters (style, color, price)
- [ ] Favorites/like functionality
- [ ] Share generated images
- [ ] User analytics

---

## 6. Implementation Phases

### Phase 1: Foundation (Days 1-2)
**Owner**: System Architect + Backend API Engineer

- [ ] Design system architecture
- [ ] Create database schema
- [ ] Set up FastAPI application
- [ ] Initialize PostgreSQL database
- [ ] Create project structure

**Deliverables:**
- Architecture document
- Database migrations
- FastAPI skeleton
- API health check endpoint

### Phase 2: Data Collection (Days 2-3)
**Owner**: Web Scraper Engineer

- [ ] Build ASOS scraper (500 products)
- [ ] Build H&M scraper (500 products)
- [ ] Build Zara scraper (500 products)
- [ ] Build Nike scraper (500 products)
- [ ] Seed database with products
- [ ] Validate all product images

**Deliverables:**
- 4 working scrapers
- 2000+ products in database
- Product validation scripts

### Phase 3: Mobile UI (Days 3-4)
**Owner**: React Native Developer

- [ ] Set up Expo Router project
- [ ] Build onboarding screen (photo upload)
- [ ] Create feed screen (FlatList)
- [ ] Build FeedCard component
- [ ] Build LoadingCard component
- [ ] Add navigation
- [ ] Integrate mock data

**Deliverables:**
- Working mobile UI
- Navigation flow
- Component library

### Phase 4: AI Integration (Days 4-5)
**Owner**: AI Integration Specialist

- [ ] Implement Rork API client
- [ ] Build product image fetcher
- [ ] Create virtual try-on generator
- [ ] Add product validation (REAL images only)
- [ ] Implement retry logic
- [ ] Add error handling

**Deliverables:**
- RorkAIClient class
- Product validator
- Base64 utilities
- Error handling framework

### Phase 5: Performance (Days 5-6)
**Owner**: Performance Engineer

- [ ] Implement 30-worker system
- [ ] Add image preloading (next 5)
- [ ] Build queue management
- [ ] Optimize scroll performance (60fps)
- [ ] Add buffer health monitoring
- [ ] Memory profiling & optimization

**Deliverables:**
- FeedLoadingService (30 workers)
- Preloading system
- Performance benchmarks

### Phase 6: Testing & Polish (Days 6-7)
**Owner**: QA & Test Engineer + Documentation Specialist

- [ ] Write unit tests (80%+ coverage)
- [ ] Create integration tests
- [ ] E2E testing (critical flows)
- [ ] Write PRD.md
- [ ] Write CLAUDE.md
- [ ] Write README.md
- [ ] Final bug fixes

**Deliverables:**
- Test suite
- Documentation
- Production-ready app

---

## 7. Risks & Mitigation

### Risk 1: AI API Failures
**Likelihood**: Medium
**Impact**: High
**Mitigation**:
- Circuit breaker pattern
- Retry logic with exponential backoff
- Try different product on failure
- Monitor API health continuously

### Risk 2: Poor Generation Quality
**Likelihood**: Medium
**Impact**: High
**Mitigation**:
- High-quality product images only
- Optimized prompt templates
- User photo quality guidelines
- Output validation

### Risk 3: Performance Degradation
**Likelihood**: Low
**Impact**: High
**Mitigation**:
- 30-worker system (not 10)
- Aggressive preloading
- Memory profiling
- Performance monitoring

### Risk 4: Insufficient Product Data
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Multiple brand sources (4+)
- Web scraper redundancy
- Image validation before seeding
- 2000+ product target

### Risk 5: Text-Only Generation Fallback
**Likelihood**: Medium
**Impact**: Critical
**Mitigation**:
- **Strict validation**: NEVER allow generation without real product image
- **Throw errors** if product missing image
- **Try different product** instead of text-only fallback
- **Comprehensive logging** to catch violations

---

## 8. Dependencies

### External Services
- **Rork API**: Gemini Flash 2.5 virtual try-on
- **Supabase**: Managed PostgreSQL hosting
- **ASOS/H&M/Zara/Nike**: Product data sources

### Internal Dependencies
- Mobile app depends on catalog API
- AI generation depends on product images
- Feed performance depends on worker system

### Critical Path
1. Catalog API must be ready before mobile development
2. Product scraping must complete before AI testing
3. AI integration must work before performance optimization

---

## 9. Open Questions

- [ ] What product categories to prioritize? (tops, bottoms, shoes, accessories)
- [ ] Should we support multiple user photos per session?
- [ ] What analytics/metrics should we track?
- [ ] Do we need user accounts (or anonymous only)?
- [ ] What's the refresh frequency for product catalog?

---

## 10. Appendix

### A. Glossary

- **Virtual Try-On**: AI-generated image of user wearing specific product
- **Worker**: Parallel AI generation process
- **Buffer Health**: Percentage of preloaded items vs total needed
- **Circuit Breaker**: Pattern to prevent API overload during failures
- **Product Validation**: Checking product has valid image URLs before generation

### B. References

- Gemini Flash 2.5 Documentation
- Rork API Documentation
- React Native Performance Guide
- FastAPI Best Practices
- PostgreSQL Optimization Guide

---

**Document Control**
**Author**: AI Team
**Reviewers**: [Pending]
**Approval**: [Pending]
**Last Updated**: 2025-10-02
