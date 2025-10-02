"""
UPLO-DB FastAPI Catalog Service
Production-ready API for serving real product catalog data to UPLO3 mobile app
"""

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from datetime import datetime
import os
import sys
import logging
import json
import httpx
from urllib.parse import unquote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('uplo-db-api')

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Custom JSON encoder for datetime and other types
def custom_json_encoder(obj):
    """Convert non-serializable objects to JSON-serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

# Import database service (with fallback for development)
try:
    from backend.database import getDatabaseService, getSyncManager
    logger.info("✅ Database services imported successfully")
except ImportError as e:
    logger.warning(f"⚠️  Database services not available: {e}")
    # Fallback implementations for development
    class MockDatabaseService:
        def get_stats(self):
            return {"brands": {}, "categories": {}, "total_products": 0}

        def search_products(self, **kwargs):
            return {"products": [], "total": 0}

        def get_product_by_id(self, product_id: int):
            return None

    class MockSyncManager:
        def get_stats(self):
            return {"last_sync": None, "total_syncs": 0}

    def getDatabaseService():
        return MockDatabaseService()

    def getSyncManager():
        return MockSyncManager()

# Initialize FastAPI app
app = FastAPI(
    title="UPLO-DB Catalog API",
    description="Real-time product catalog service for UPLO3 fashion app",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# Mount static files for serving product images
# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to get to catalog-service root, then into static
static_dir = os.path.join(current_dir, '..', '..', 'static')
logger.info(f"📁 Mounting static files from: {static_dir}")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info("✅ Static files mounted at /static")
else:
    logger.warning(f"⚠️  Static directory not found: {static_dir}")

# CORS configuration - Allow all origins for now (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to UPLO3 app domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache control middleware for CDN optimization
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)

    # Set cache headers for GET requests
    if request.method == "GET":
        # Cache feed and product endpoints for 60 minutes
        if "/feed" in request.url.path or "/product/" in request.url.path:
            response.headers["Cache-Control"] = "public, max-age=3600"  # 1 hour
            response.headers["CDN-Cache-Control"] = "public, max-age=3600"

        # Cache health and stats for 5 minutes only
        elif "/health" in request.url.path or "/stats" in request.url.path:
            response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes

    # Add catalog version header for cache invalidation
    db = getDatabaseService()
    stats = db.get_stats()
    if hasattr(stats, 'last_updated'):
        response.headers["X-Catalog-Version"] = str(stats.last_updated)

    return response

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    Returns database connection status and last scrape time
    """
    try:
        db = getDatabaseService()
        sync_manager = getSyncManager()

        stats = db.get_stats()
        sync_stats = sync_manager.get_stats()

        return {
            "status": "healthy",
            "database": "connected",
            "catalog_size": stats.get("total_products", 0),
            "last_scrape": sync_stats.get("last_sync"),
            "uptime_seconds": 0,  # TODO: Track actual uptime
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Statistics endpoint
@app.get("/api/v1/stats")
async def get_stats():
    """
    Get catalog statistics
    Returns counts by brand, category, and last update time
    """
    try:
        db = getDatabaseService()
        stats = db.get_stats()

        return {
            "total_products": stats.get("total_products", 0),
            "total_brands": len(stats.get("brands", {})),
            "by_brand": stats.get("brands", {}),
            "by_category": stats.get("categories", {}),
            "last_updated": stats.get("last_updated", datetime.utcnow().isoformat())
        }
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

# Image proxy endpoint to bypass ASOS CDN restrictions
@app.get("/api/v1/proxy-image")
async def proxy_image(
    url: str = Query(..., description="Image URL to proxy")
):
    """
    Proxy images from ASOS and other CDNs to bypass iOS Simulator restrictions.
    This endpoint fetches the image with proper headers and streams it back to the client.
    """
    try:
        # Decode the URL if it's encoded
        image_url = unquote(url)

        logger.info(f"🖼️  Proxying image: {image_url}")

        # Validate that it's an image URL
        valid_domains = [
            'images.asos-media.com',
            'lp2.hm.com',
            'static.zara.net',
            'images.nike.com',
            'assets.adidas.com',
            'via.placeholder.com',
            'placeholder.com',
        ]

        # Check if the URL is from a valid domain
        is_valid = any(domain in image_url for domain in valid_domains)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid image URL domain")

        # Fetch the image with proper headers to bypass restrictions
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                image_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.asos.com/',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'cross-site',
                }
            )

            if response.status_code != 200:
                logger.error(f"❌ Image fetch failed: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch image")

            # Stream the image back with appropriate headers
            return StreamingResponse(
                iter([response.content]),
                media_type=response.headers.get('content-type', 'image/jpeg'),
                headers={
                    'Cache-Control': 'public, max-age=86400',  # Cache for 24 hours
                    'Access-Control-Allow-Origin': '*',
                }
            )

    except httpx.TimeoutException:
        logger.error(f"⏰ Image fetch timeout: {image_url}")
        raise HTTPException(status_code=504, detail="Image fetch timeout")
    except Exception as e:
        logger.error(f"❌ Image proxy failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image proxy error: {str(e)}")

@app.get("/api/v1/feed")
async def get_feed(
    limit: int = Query(100, ge=1, le=100, description="Items per page (max 100)"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    in_stock: bool = Query(True, description="Only show in-stock items"),
):
    """Get paginated product feed"""
    try:
        db = getDatabaseService()
        result = db.get_feed(
            limit=limit,
            cursor=cursor,
            brand=brand,
            category=category,
            in_stock=in_stock
        )

        response_data = {
            "items": result['items'],
            "next_cursor": result.get('next_cursor'),
            "catalog_version": "1.0",
            "total_count": len(result['items']),
            "timestamp": datetime.now().isoformat()
        }

        # Use custom JSON encoder to handle datetime objects
        json_content = json.dumps(response_data, default=custom_json_encoder)
        return JSONResponse(content=json.loads(json_content))

    except Exception as e:
        logger.error(f"Feed retrieval failed: {e}", exc_info=True)
        # Return more detailed error info for debugging
        error_detail = f"Failed to retrieve feed: {str(e)}"
        raise HTTPException(status_code=500, detail=error_detail)

# Import and register route modules
try:
    from .routes import feed, products
    app.include_router(feed.router, prefix="/api/v1")
    app.include_router(products.router, prefix="/api/v1")
    logger.info("✅ API routes registered: /api/v1/feed, /api/v1/product/:id")
except ImportError as e:
    logger.warning(f"⚠️  Could not import routes (routes will not be available): {e}")

# Root redirect
@app.get("/")
async def root():
    """Redirect root to API documentation"""
    return JSONResponse({
        "message": "UPLO-DB Catalog API",
        "version": "1.0.1-fix-json-serialization",  # Updated version to track deployment
        "docs": "/api/v1/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "feed": "/api/v1/feed",
            "product_detail": "/api/v1/product/{id}",
            "stats": "/api/v1/stats"
        }
    })

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 UPLO-DB Catalog API starting up...")
    logger.info(f"📊 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"🗄️  Database: {os.getenv('DATABASE_URL', 'Not configured')[:30]}...")

    # Test database connection
    try:
        db = getDatabaseService()
        stats = db.get_stats()
        logger.info(f"✅ Database connected - {stats.get('total_products', 0)} products in catalog")
    except Exception as e:
        logger.warning(f"⚠️  Database connection failed (will use fallback): {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 UPLO-DB Catalog API shutting down...")

if __name__ == "__main__":
    import uvicorn

    # Development server
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
