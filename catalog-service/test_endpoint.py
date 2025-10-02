#!/usr/bin/env python3
"""Test the FastAPI endpoint directly"""

import sys
import os

# Set database URL
os.environ['DATABASE_URL'] = 'postgresql://postgres.fvpkhmtdvllnaazvlkah:AppleB4nanaxx@aws-1-eu-west-2.pooler.supabase.com:6543/postgres'

# Test the endpoint
from backend.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("🔍 Testing /api/v1/feed endpoint...")
print("-" * 50)

try:
    response = client.get('/api/v1/feed?limit=5')
    print(f'Status: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        print(f'✅ Success! Got {len(data["items"])} items')
        print(f'First item: {data["items"][0]["name"]}')
        print(f'Next cursor: {data.get("next_cursor")}')
    else:
        print(f'❌ Error: {response.text}')
        print(f'Response: {response.json()}')

except Exception as e:
    print(f'❌ Exception: {e}')
    import traceback
    traceback.print_exc()
