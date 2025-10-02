#!/usr/bin/env python3
"""Test script to debug get_feed() query"""

import sys
import os

# Set database URL
os.environ['DATABASE_URL'] = 'postgresql://postgres.fvpkhmtdvllnaazvlkah:AppleB4nanaxx@aws-1-eu-west-2.pooler.supabase.com:6543/postgres'

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.service import getDatabaseService

db = getDatabaseService()

print("🔍 Testing get_feed() query...")
print("-" * 50)

try:
    result = db.get_feed(limit=5, in_stock=False)  # Get all products, even out of stock
    print('✅ Query successful!')
    print(f'Items returned: {len(result["items"])}')
    print(f'Next cursor: {result.get("next_cursor")}')

    if result['items']:
        print("\n📦 First item:")
        first_item = result['items'][0]
        for key, value in first_item.items():
            print(f"  {key}: {value}")
    else:
        print("\n⚠️  No items returned!")

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
