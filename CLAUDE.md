# CLAUDE.md

This file provides comprehensive guidance to AI assistants (Claude Code, Claude, etc.) when working with code in this repository.

---

## 🎯 Project Overview

**UPLO5** is a TikTok-style virtual try-on fashion app featuring:
- **AI-powered virtual try-on** using Gemini Flash 2.5 via Rork API
- **Real product integration** from ASOS, H&M, Zara, Nike
- **30-worker parallel AI generation** with infinite scroll
- **React Native + Expo Router** mobile app
- **FastAPI + PostgreSQL** catalog backend

**Platform**: Cross-platform (iOS, Android, Web) via Expo
**Repository**: https://github.com/RooJenkins/UPLO5

---

## 🚨 CRITICAL REQUIREMENTS (READ FIRST!)

### 1. REAL PRODUCT IMAGES ONLY (NON-NEGOTIABLE!)

**NEVER generate virtual try-on without a real product image!**

```typescript
// ✅ CORRECT - Always fetch and use real product image
const product = await fetchProduct();
if (!product.image_urls || product.image_urls.length === 0) {
  throw new Error('Product missing image - cannot generate');
}
const productImageBase64 = await fetchAndConvertToBase64(product.image_urls[0]);
await rorkAPI.generate({
  userImage: userBase64,
  productImage: productImageBase64 // MUST be real!
});

// ❌ FORBIDDEN - Never use text-only prompts
await rorkAPI.generate({
  prompt: "put blue jeans on person" // NO!
});
```

**Validation Checklist Before EVERY Generation:**
- [ ] Product object exists
- [ ] `product.image_urls` is array
- [ ] `product.image_urls.length > 0`
- [ ] `product.image_urls[0]` starts with `http`
- [ ] Product image successfully fetched
- [ ] Product image converted to base64
- [ ] Both user image AND product image sent to API

### 2. 30 Workers Required (Not 10!)

The system MUST use **30 parallel workers** for AI generation, not 10.

**Check worker count displays "30/30" in LoadingStats component.**

---

## 📋 TODO Task Management (MANDATORY)

### When to Use TodoWrite Tool

**ALWAYS create TODO lists for:**
- Complex multi-step tasks (3+ steps)
- User provides multiple instructions
- User adds requests mid-task
- Planning implementations
- Debugging complex issues

**TODO List Discipline:**
1. Create list at task start
2. Mark tasks `in_progress` when starting
3. Update `completed` IMMEDIATELY after finishing
4. Keep exactly ONE task `in_progress` at a time
5. Update list if user sends new instructions

**Example Workflow:**
```typescript
// User: "Build catalog API and write tests"
TodoWrite({
  todos: [
    { content: "Build FastAPI catalog service", status: "in_progress", activeForm: "Building catalog service" },
    { content: "Write unit tests", status: "pending", activeForm: "Writing unit tests" }
  ]
});

// After completing first task
TodoWrite({
  todos: [
    { content: "Build FastAPI catalog service", status: "completed", activeForm: "Building catalog service" },
    { content: "Write unit tests", status: "in_progress", activeForm: "Writing unit tests" }
  ]
});
```

---

## 👥 Agent Team Structure

All agents use **Sonnet 4.5** (claude-sonnet-4-5-20250929).

### Agent Definitions
Located in `.claude/agents/sonnet/`:

1. **system-architect.md** - Architecture, database schema, API design
2. **backend-api-engineer.md** - FastAPI, PostgreSQL, REST APIs
3. **web-scraper-engineer.md** - Product data extraction (ASOS, H&M, Zara, Nike)
4. **react-native-developer.md** - Mobile UI, components, navigation
5. **ai-integration-specialist.md** - Rork API, virtual try-on, image processing
6. **performance-engineer.md** - 30-worker system, preloading, 60fps optimization
7. **qa-test-engineer.md** - Testing (unit, integration, E2E)
8. **documentation-specialist.md** - PRD, README, API docs

### Agent Coordination

**Phase 1: Foundation**
- System Architect → designs architecture
- Backend API Engineer → implements FastAPI

**Phase 2: Data Collection**
- Web Scraper Engineer → scrapes 2000+ products

**Phase 3: Mobile UI**
- React Native Developer → builds app UI

**Phase 4: AI Integration**
- AI Integration Specialist → implements Rork API

**Phase 5: Performance**
- Performance Engineer → 30 workers + preloading

**Phase 6: Quality**
- QA Engineer → comprehensive testing
- Documentation Specialist → PRD, CLAUDE.md, README

---

## 💻 Development Commands

### Mobile App (React Native + Expo)

```bash
# Navigate to project root
cd /Users/roo/UPLO5

# Install dependencies
npm install
# or
bun install

# Start development server
npx expo start

# Start with clear cache
npx expo start --clear

# Platform-specific
npx expo start --ios
npx expo start --android
npx expo start --web

# Type check
npx tsc --noEmit

# Lint
npx expo lint
```

### Catalog Service (Python Backend)

```bash
# Navigate to catalog service
cd catalog-service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run database migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8000

# Run scrapers
python -m scraper.run --source asos --limit 500
python -m scraper.run --source hm --limit 500
python -m scraper.run --source zara --limit 500
python -m scraper.run --source nike --limit 500

# Run all scrapers
python -m scraper.run --all --limit 500

# Run tests
pytest
pytest --cov=app tests/
```

---

## 🏗️ Architecture Deep Dive

### Directory Structure

```
UPLO5/
├── .claude/
│   └── agents/
│       └── sonnet/          # All 8 agent definitions
├── app/                     # React Native app
│   ├── (main)/
│   │   └── feed.tsx         # Main feed screen
│   ├── _layout.tsx          # Root layout
│   ├── index.tsx            # Entry point
│   └── onboarding.tsx       # Photo upload
├── catalog-service/         # Python backend
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # SQLAlchemy models
│   │   └── database.py      # DB connection
│   ├── scraper/
│   │   ├── sources/
│   │   │   ├── asos.py
│   │   │   ├── hm.py
│   │   │   ├── zara.py
│   │   │   └── nike.py
│   │   └── run.py           # Scraper CLI
│   ├── alembic/             # Migrations
│   └── tests/
├── components/              # Reusable UI components
│   ├── FeedCard.tsx
│   ├── LoadingCard.tsx
│   └── ProductCard.tsx
├── lib/                     # Core services
│   ├── RorkAIClient.ts      # Rork API integration
│   ├── FeedLoadingService.ts # 30-worker system
│   └── ProductValidator.ts
├── providers/               # React Context
│   ├── FeedProvider.tsx     # Feed state + worker orchestration
│   └── UserProvider.tsx     # User photo storage
├── PRD.md                   # Product requirements
├── CLAUDE.md                # This file
├── README.md                # Project overview
└── package.json
```

### Database Schema

```sql
-- Products table (CRITICAL: image_urls required)
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  product_id INTEGER UNIQUE NOT NULL,
  name VARCHAR(500) NOT NULL,
  brand_name VARCHAR(200) NOT NULL,
  image_urls TEXT[] NOT NULL,        -- MUST have at least one image
  base_price INTEGER,                 -- Price in cents
  currency VARCHAR(3) DEFAULT 'USD',
  category VARCHAR(100),
  available_sizes TEXT[],
  available_colors TEXT[],
  product_url VARCHAR(1000),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Ensure all products have images
CREATE INDEX idx_products_brand ON products(brand_name);
CREATE INDEX idx_products_category ON products(category);
ALTER TABLE products ADD CONSTRAINT check_has_images
  CHECK (array_length(image_urls, 1) > 0);
```

### API Endpoints

**Catalog API** (port 8000):

```
GET  /api/v1/products/random   # Get random product
GET  /api/v1/products           # List products (paginated)
GET  /api/v1/products/{id}      # Get specific product
GET  /api/v1/health             # Health check
GET  /api/v1/stats              # Catalog statistics
```

**Rork AI API**:

```
POST https://toolkit.rork.com/images/edit/

Request:
{
  "prompt": "Professional fashion photoshoot...",
  "images": [
    { "type": "image", "image": "<user_base64>" },
    { "type": "image", "image": "<product_base64>" }
  ]
}

Response:
{
  "image": {
    "base64Data": "<generated_base64>",
    "mimeType": "image/jpeg"
  }
}
```

---

## 🔥 Critical Patterns & Best Practices

### 1. Product Validation Pattern

**ALWAYS validate before generation:**

```typescript
function validateProductForGeneration(product: any): boolean {
  if (!product) {
    console.error('[VALIDATION] ❌ No product provided');
    return false;
  }

  if (!Array.isArray(product.image_urls)) {
    console.error('[VALIDATION] ❌ Missing image_urls array');
    return false;
  }

  if (product.image_urls.length === 0) {
    console.error('[VALIDATION] ❌ Empty image_urls array');
    return false;
  }

  const imageUrl = product.image_urls[0];
  if (!imageUrl || !imageUrl.startsWith('http')) {
    console.error('[VALIDATION] ❌ Invalid image URL:', imageUrl);
    return false;
  }

  console.log('[VALIDATION] ✅ Product valid for generation');
  return true;
}
```

### 2. Rork API Integration Pattern

```typescript
// lib/RorkAIClient.ts

export class RorkAIClient {
  private readonly API_URL = 'https://toolkit.rork.com/images/edit/';
  private readonly MAX_RETRIES = 3;

  async generateVirtualTryOn(params: {
    userImageBase64: string;
    product: Product;
  }): Promise<string> {
    // Step 1: Validate product
    if (!validateProductForGeneration(params.product)) {
      throw new Error('Product validation failed');
    }

    // Step 2: Fetch product image
    const productImageBase64 = await this.fetchProductImage(
      params.product.image_urls[0]
    );

    // Step 3: Build prompt
    const prompt = this.buildPrompt(params.product);

    // Step 4: Call API with retry
    return await this.retryWithBackoff(async () => {
      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          images: [
            { type: 'image', image: params.userImageBase64 },
            { type: 'image', image: productImageBase64 }
          ]
        })
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const data = await response.json();
      return `data:${data.image.mimeType};base64,${data.image.base64Data}`;
    });
  }

  private buildPrompt(product: Product): string {
    return `Create a professional fashion photoshoot showing the person wearing the exact ${product.name} by ${product.brand_name} from the reference product image.

CRITICAL REQUIREMENTS:
- Transfer the EXACT clothing item from product image onto person
- Maintain clothing's color, style, fit, and details from product
- Keep person's face, body, and pose recognizable
- Professional white/neutral background
- Studio lighting and fashion photography composition
- Full body shot with model's head at 35-40% from top

The result must look like a professional product photoshoot with the real item.`;
  }

  private async fetchProductImage(url: string): Promise<string> {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Failed to fetch: ${response.status}`);
    const blob = await response.blob();
    return await this.blobToBase64(blob);
  }

  private async blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        resolve(result.split(',')[1]);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  private async retryWithBackoff<T>(
    fn: () => Promise<T>,
    retries = this.MAX_RETRIES
  ): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      if (retries === 0) throw error;
      await new Promise(r => setTimeout(r, 1000 * (4 - retries)));
      return this.retryWithBackoff(fn, retries - 1);
    }
  }
}
```

### 3. 30-Worker System Pattern

```typescript
// lib/FeedLoadingService.ts

export class FeedLoadingService {
  private readonly MAX_WORKERS = 30;  // NOT 10!
  private readonly BUFFER_TARGET = 30;
  private activeWorkers = 0;
  private jobQueue: Job[] = [];

  async processQueue(userImageBase64: string) {
    while (this.activeWorkers < this.MAX_WORKERS && this.jobQueue.length > 0) {
      const job = this.jobQueue.shift();
      if (!job) continue;

      this.activeWorkers++;
      this.processJob(job, userImageBase64)
        .finally(() => this.activeWorkers--);
    }
  }

  private async processJob(job: Job, userImageBase64: string) {
    try {
      // Fetch product from catalog
      const product = await this.fetchProduct();

      // Generate with REAL product image
      const rorkClient = new RorkAIClient();
      const generatedImage = await rorkClient.generateVirtualTryOn({
        userImageBase64,
        product
      });

      // Cache result
      this.imageCache.set(job.position, {
        id: job.id,
        imageUrl: generatedImage,
        product,
        position: job.position
      });

    } catch (error) {
      console.error('[WORKER] Generation failed:', error);
      // Try different product instead of text-only fallback
      const differentProduct = await this.fetchDifferentProduct();
      // Retry with different product...
    }
  }
}
```

### 4. Error Handling Pattern

```typescript
// NEVER fall back to text-only generation!

async function generateWithFallback(userBase64: string, product: Product) {
  try {
    if (!validateProductForGeneration(product)) {
      throw new Error('Invalid product');
    }
    return await rorkClient.generate({ userBase64, product });
  } catch (error) {
    // ✅ CORRECT: Try different product
    const nextProduct = await fetchDifferentProduct();
    if (validateProductForGeneration(nextProduct)) {
      return await rorkClient.generate({ userBase64, product: nextProduct });
    }

    // ❌ NEVER do this:
    // return await rorkClient.generateTextOnly(prompt);

    throw new Error('No valid products available');
  }
}
```

---

## 🧪 Testing Strategy

### Unit Tests (Jest)

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Specific file
npm test RorkAIClient.test.ts
```

**Required Coverage**: 80%+

**Test Files**:
- `lib/__tests__/RorkAIClient.test.ts`
- `lib/__tests__/ProductValidator.test.ts`
- `lib/__tests__/FeedLoadingService.test.ts`
- `components/__tests__/FeedCard.test.tsx`

### Integration Tests (pytest)

```bash
# Run backend tests
cd catalog-service
pytest

# With coverage
pytest --cov=app tests/

# Specific test
pytest tests/test_api.py::test_random_product
```

### E2E Tests (Detox)

```bash
# Build app for testing
detox build --configuration ios.sim.debug

# Run E2E tests
detox test --configuration ios.sim.debug
```

---

## 🚀 Performance Requirements

### Targets (Non-Negotiable)

| Metric | Target | How to Verify |
|--------|--------|---------------|
| Worker Count | 30 active | LoadingStats component shows "30/30" |
| Scroll FPS | 60fps | React DevTools profiler |
| Buffer Health | 80%+ | LoadingStats component |
| Generation Time | <3s avg | Console logs `[WORKER]` |
| Preload Count | Next 5 | Verify Image.prefetch() calls |
| Memory Usage | <200MB | Xcode Instruments / Android Profiler |

### Performance Checks

```bash
# React Native performance
npx react-native-performance-monitor

# Memory profiling (iOS)
# Use Xcode Instruments → Allocations

# Memory profiling (Android)
# Use Android Studio Profiler

# Bundle size
npx expo customize metro.config.js
# Check output bundle size
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Workers Showing 10/10 Instead of 30/30

**Cause**: Wrong MAX_WORKERS value in FeedLoadingService
**Solution**:
```typescript
// lib/FeedLoadingService.ts
private readonly MAX_WORKERS = 30; // NOT 10!
```

### Issue 2: Text-Only Generation Fallback

**Cause**: Missing product validation or incorrect error handling
**Solution**: Use product validation checklist, never allow text-only

### Issue 3: Images Not Preloading

**Cause**: Image.prefetch() not called for next 5 items
**Solution**:
```typescript
// Preload next 5 when user scrolls
useEffect(() => {
  const nextPositions = [
    currentIndex + 1,
    currentIndex + 2,
    currentIndex + 3,
    currentIndex + 4,
    currentIndex + 5
  ];

  nextPositions.forEach(pos => {
    const item = feed[pos];
    if (item?.imageUrl) {
      Image.prefetch(item.imageUrl);
    }
  });
}, [currentIndex, feed]);
```

### Issue 4: Scroll Performance < 60fps

**Causes**:
- Too many items rendered at once
- Heavy components not memoized
- Large images not optimized

**Solutions**:
```typescript
// FlatList optimization
<FlatList
  windowSize={3}
  maxToRenderPerBatch={2}
  removeClippedSubviews={true}
  getItemLayout={getItemLayout}
/>

// Component memoization
export const FeedCard = React.memo(({ entry }) => {
  // ...
});
```

### Issue 5: Product Missing Images

**Cause**: Scraper not validating image URLs
**Solution**: Add validation in scraper:
```python
def validate_product(product_data):
    if not product_data.get('image_urls'):
        return False
    if not isinstance(product_data['image_urls'], list):
        return False
    if len(product_data['image_urls']) == 0:
        return False
    if not product_data['image_urls'][0].startswith('http'):
        return False
    return True
```

---

## 📝 Code Quality Standards

### TypeScript

- **Strict mode** enabled
- **No `any` types** (use `unknown` instead)
- **Explicit return types** for functions
- **Interface over type** for objects

```typescript
// ✅ GOOD
interface Product {
  name: string;
  brand_name: string;
  image_urls: string[];
}

function getProduct(id: number): Promise<Product> {
  // ...
}

// ❌ BAD
const getProduct = (id: any): any => {
  // ...
};
```

### Python

- **Type hints** for all functions
- **Pydantic models** for validation
- **Docstrings** for classes/functions
- **PEP 8** formatting

```python
# ✅ GOOD
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    brand_name: str
    image_urls: list[str]
    base_price: int

async def get_product(product_id: int) -> Product:
    """Fetch product by ID from database."""
    # ...

# ❌ BAD
def get_product(id):
    # ...
```

### React Components

```typescript
// ✅ GOOD - Functional component with TypeScript
interface FeedCardProps {
  entry: FeedEntry;
  isActive: boolean;
}

export const FeedCard: React.FC<FeedCardProps> = ({ entry, isActive }) => {
  // Use hooks
  const [isLoaded, setIsLoaded] = useState(false);

  // Memoize expensive calculations
  const imageStyle = useMemo(() => ({
    width: '100%',
    height: SCREEN_HEIGHT
  }), []);

  return (
    <View>
      {/* ... */}
    </View>
  );
};

// Memoize component
export default React.memo(FeedCard);
```

---

## 🔧 Git Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/agent-name-feature` - Feature branches
- `fix/bug-description` - Bug fixes

### Commit Convention

```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
Scopes: backend, mobile, scraper, ai, perf, docs

Examples:
feat(ai): implement Rork API client with product validation
fix(backend): ensure all products have valid image URLs
docs(readme): add setup instructions for catalog service
test(mobile): add unit tests for FeedCard component
```

### Commit Checklist

Before committing:
- [ ] Code follows style guide
- [ ] All tests pass (`npm test`, `pytest`)
- [ ] Type check passes (`npx tsc --noEmit`)
- [ ] Lint passes (`npx expo lint`)
- [ ] No console.log statements (use proper logging)
- [ ] Documentation updated if needed

---

## 📊 Monitoring & Debugging

### Console Log Prefixes

Use these prefixes for organized logging:

- `[AI-VALIDATION]` - Product validation
- `[AI-CLIENT]` - Rork API calls
- `[WORKER]` - Worker pool operations
- `[FEED]` - Feed state management
- `[FEEDCARD]` - Component rendering
- `[SCRAPER]` - Web scraping operations
- `[API]` - Backend API operations

**Example**:
```typescript
console.log('[AI-VALIDATION] ✅ Product valid:', product.name);
console.error('[AI-CLIENT] ❌ API call failed:', error);
console.log('[WORKER] 🔄 Processing job at position', position);
```

### Debug Mode

Enable verbose logging:
```typescript
// .env.local
EXPO_PUBLIC_DEBUG=true
EXPO_PUBLIC_LOG_LEVEL=verbose
```

---

## 🎓 Learning Resources

### React Native
- [React Native Docs](https://reactnative.dev/docs/getting-started)
- [Expo Docs](https://docs.expo.dev/)
- [Expo Router](https://expo.github.io/router/docs/)

### FastAPI
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic](https://docs.pydantic.dev/)

### Testing
- [Jest Docs](https://jestjs.io/docs/getting-started)
- [React Native Testing Library](https://callstack.github.io/react-native-testing-library/)
- [Pytest Docs](https://docs.pytest.org/)

---

## ✅ Pre-Launch Checklist

Before considering the app complete:

### Functionality
- [ ] User can upload photo
- [ ] Feed loads and displays generated images
- [ ] Every generation uses REAL product image
- [ ] 30 workers active (not 10)
- [ ] Infinite scroll works smoothly
- [ ] Preloading next 5 items
- [ ] "Shop Now" button works
- [ ] Product details display correctly

### Performance
- [ ] 60fps scroll performance
- [ ] <3s average generation time
- [ ] 80%+ buffer health
- [ ] <200MB memory usage
- [ ] No memory leaks

### Quality
- [ ] 80%+ test coverage
- [ ] All tests passing
- [ ] No TypeScript errors
- [ ] No ESLint warnings
- [ ] Documentation complete

### Data
- [ ] 2000+ products in database
- [ ] All products have valid images
- [ ] Product URLs work
- [ ] Prices formatted correctly

---

## 🤝 Agent Handoff Protocol

When handing off between agents:

1. **Complete current task fully**
2. **Update TODO list**
3. **Document what was done**
4. **Note any blockers**
5. **Specify next steps**
6. **Commit changes if appropriate**

**Example Handoff**:
```
[System Architect to Backend Engineer]

✅ Completed:
- Architecture design document
- Database schema created
- API contract defined
- Project structure initialized

📋 Handoff:
- Database schema ready for implementation
- FastAPI skeleton needs completion
- See `docs/architecture.md` for full specs

🚧 Next Steps:
1. Implement FastAPI application
2. Set up SQLAlchemy models
3. Create database migrations
4. Implement `/products/random` endpoint

📁 Files Modified:
- docs/architecture.md
- catalog-service/database/schema.sql
```

---

**Remember**: This is a production app. Quality, performance, and user experience are paramount. Follow all patterns strictly, especially the REAL PRODUCT IMAGES ONLY requirement. When in doubt, validate, test, and verify.

**Happy Coding! 🚀**
