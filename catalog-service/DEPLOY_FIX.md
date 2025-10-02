# Feed Endpoint Fix - Deployment Instructions

## Issue Fixed
The `/api/v1/feed` endpoint was failing with "Feed query failed" error due to JSON serialization issues.

## Changes Made

### 1. backend/database/service.py
**Problem**: The `get_feed()` method was returning psycopg2's `RealDictRow` objects which don't serialize properly to JSON.

**Fix**: Convert RealDictRow objects to regular Python dictionaries before returning:
```python
# Convert RealDictRow objects to regular dicts for JSON serialization
items_list = [dict(item) for item in items]

return {
    'items': items_list,
    'next_cursor': next_cursor
}
```

### 2. backend/api/main.py
**Problem**: DateTime objects in the response weren't being serialized properly.

**Fix**: Added custom JSON encoder to handle datetime objects:
```python
def custom_json_encoder(obj):
    """Convert non-serializable objects to JSON-serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
```

And updated the endpoint to use it:
```python
# Use custom JSON encoder to handle datetime objects
json_content = json.dumps(response_data, default=custom_json_encoder)
return JSONResponse(content=json.loads(json_content))
```

## Testing

### Local Testing (PASSED ✅)
```bash
# Test direct database query
python3 test_feed.py
# Result: ✅ Query successful! Items returned: 5

# Test JSON serialization
python3 test_feed_json.py
# Result: ✅ JSON serialization successful!

# Test FastAPI endpoint
python3 test_endpoint.py
# Result: ✅ Status: 200, Got 5 items

# Test running server
curl "http://localhost:8000/api/v1/feed?limit=5"
# Result: ✅ Returns JSON with 5 products
```

## Deployment Status

**Code Status**: ✅ Fixed and committed to main branch (commit: 81ed828)
**Railway Status**: ⚠️ NOT YET DEPLOYED

Railway is not auto-deploying the changes. The production API still shows version "1.0.0" instead of "1.0.1-fix-json-serialization".

## Manual Deployment Steps

### Option 1: Railway Dashboard
1. Go to https://railway.app/dashboard
2. Find the "uplo3-catalog-api-production" project
3. Trigger a manual deployment from the main branch
4. Verify the root directory is set to `catalog-service/` or the correct path

### Option 2: Railway CLI
```bash
# Install Railway CLI if needed
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy from catalog-service directory
cd /Users/roo/UPLO3/catalog-service
railway up
```

### Option 3: Force GitHub Webhook
If Railway is connected via GitHub webhook:
1. Check Railway project settings for GitHub integration
2. Ensure the root directory is configured as `/catalog-service`
3. Try making a small change and pushing to trigger deployment

## Verification

After deployment, run these commands to verify the fix:

```bash
# Check version (should show 1.0.1-fix-json-serialization)
curl "https://uplo3-catalog-api-production.up.railway.app/"

# Check health
curl "https://uplo3-catalog-api-production.up.railway.app/api/v1/health"

# Test feed endpoint (should return JSON with products)
curl "https://uplo3-catalog-api-production.up.railway.app/api/v1/feed?limit=5"

# Expected response:
# {
#     "items": [
#         {
#             "product_id": 1,
#             "brand_name": "ASOS",
#             "name": "ASOS DESIGN skinny jeans...",
#             ...
#         }
#     ],
#     "next_cursor": "5",
#     "total_count": 5,
#     ...
# }
```

## What Was The Bug?

The bug had two parts:

1. **Database Layer**: The `get_feed()` method in `backend/database/service.py` was returning psycopg2's `RealDictRow` objects directly. While these objects act like dictionaries, they're not plain Python dicts and don't serialize to JSON properly in all contexts.

2. **API Layer**: The FastAPI endpoint was trying to serialize datetime objects (from the `updated_at` field) without a custom encoder. Python's default JSON serializer doesn't handle datetime objects.

## Files Changed
- `/Users/roo/UPLO3/catalog-service/backend/database/service.py` - Added dict conversion
- `/Users/roo/UPLO3/catalog-service/backend/api/main.py` - Added custom JSON encoder
- `/Users/roo/UPLO3/catalog-service/Procfile` - Added for deployment
- `/Users/roo/UPLO3/catalog-service/railway.json` - Added for Railway config

All changes have been committed to the main branch and are ready for deployment.
