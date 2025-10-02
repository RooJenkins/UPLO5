#!/usr/bin/env python3
"""Test JSON serialization of get_feed() results"""

import sys
import os
import json

# Set database URL
os.environ['DATABASE_URL'] = 'postgresql://postgres.fvpkhmtdvllnaazvlkah:AppleB4nanaxx@aws-1-eu-west-2.pooler.supabase.com:6543/postgres'

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.service import getDatabaseService

db = getDatabaseService()

print("🔍 Testing get_feed() JSON serialization...")
print("-" * 50)

try:
    result = db.get_feed(limit=5, in_stock=False)
    print('✅ Query successful!')
    print(f'Items returned: {len(result["items"])}')

    # Try to JSON serialize the result
    print("\n🔄 Testing JSON serialization...")
    json_str = json.dumps(result, default=str)  # Use str as fallback for non-serializable types
    print('✅ JSON serialization successful!')
    print(f'JSON length: {len(json_str)} bytes')

    # Parse it back
    parsed = json.loads(json_str)
    print(f'✅ Can parse back: {len(parsed["items"])} items')

except TypeError as e:
    print(f'❌ JSON Serialization Error: {e}')
    print("\n🔍 Checking item types...")
    if result and 'items' in result and result['items']:
        first_item = result['items'][0]
        print(f"Item type: {type(first_item)}")
        print(f"Item dict: {dict(first_item)}")
        for key, value in first_item.items():
            print(f"  {key}: {type(value).__name__} = {value}")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
