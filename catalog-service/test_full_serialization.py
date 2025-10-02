#!/usr/bin/env python3
"""Test full JSON serialization of feed endpoint response"""

import sys
import os
import json

# Set database URL
os.environ['DATABASE_URL'] = 'postgresql://postgres.fvpkhmtdvllnaazvlkah:AppleB4nanaxx@aws-1-eu-west-2.pooler.supabase.com:6543/postgres'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.service import getDatabaseService
from datetime import datetime

# Custom JSON encoder
def custom_json_encoder(obj):
    """Convert non-serializable objects to JSON-serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

db = getDatabaseService()

print("🔍 Testing full feed serialization...")
print("-" * 50)

try:
    # Get feed data
    result = db.get_feed(limit=5, in_stock=False)
    print(f'✅ Got {len(result["items"])} items from database')

    # Build response like the endpoint does
    response_data = {
        "items": result['items'],
        "next_cursor": result.get('next_cursor'),
        "catalog_version": "1.0",
        "total_count": len(result['items']),
        "timestamp": datetime.now().isoformat()
    }

    # Try to serialize
    print("\n🔄 Testing JSON serialization...")
    json_content = json.dumps(response_data, default=custom_json_encoder)
    print(f'✅ Serialization successful! Length: {len(json_content)} bytes')

    # Parse it back
    parsed = json.loads(json_content)
    print(f'✅ Can parse back: {len(parsed["items"])} items')

    # Print first item to verify structure
    print(f'\n📦 First item keys: {list(parsed["items"][0].keys())}')
    print(f'First item name: {parsed["items"][0]["name"]}')

except TypeError as e:
    print(f'❌ JSON Serialization Error: {e}')
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
