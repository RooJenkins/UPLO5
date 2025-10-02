"""
Fetch REAL ASOS product images using ASOS API
This will get actual product data with real images
"""
import requests
import json

# Real ASOS product IDs from their website
real_asos_products = [
    201527528,  # ASOS DESIGN oversized t-shirt
    206148577,  # ASOS DESIGN skinny jeans
    205859866,  # ASOS DESIGN midi dress
    206059819,  # ASOS DESIGN hoodie
    205995707,  # ASOS DESIGN cargo pants
    206038647,  # ASOS DESIGN blazer
    205969153,  # ASOS DESIGN leather jacket
    206026315,  # ASOS DESIGN wide leg jeans
    205907291,  # ASOS DESIGN maxi dress
    206071429,  # ASOS DESIGN crop top
]

def fetch_asos_product(product_id):
    """Fetch real ASOS product data"""
    try:
        # ASOS API endpoint
        url = f"https://www.asos.com/api/product/catalogue/v3/stockprice?productIds={product_id}&store=US&currency=USD"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"✅ Fetched product {product_id}")
                print(f"   {json.dumps(data[0] if isinstance(data, list) else data, indent=2)[:500]}")
                return data[0] if isinstance(data, list) else data
        else:
            print(f"❌ Failed to fetch {product_id}: {response.status_code}")

    except Exception as e:
        print(f"❌ Error fetching {product_id}: {e}")

    return None

# Try alternative: search for products
def search_asos_products(query="jeans"):
    """Search ASOS for products"""
    try:
        url = f"https://www.asos.com/api/product/search/v2/categories/2623?q={query}&limit=10"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search results for '{query}':")
            print(json.dumps(data, indent=2)[:1000])
            return data
        else:
            print(f"❌ Search failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Search error: {e}")

    return None

if __name__ == "__main__":
    print("=" * 80)
    print("FETCHING REAL ASOS PRODUCTS")
    print("=" * 80)
    print()

    # Try fetching products
    for pid in real_asos_products[:3]:
        product = fetch_asos_product(pid)
        print()

    # Try search
    print("\n" + "=" * 80)
    print("SEARCHING ASOS PRODUCTS")
    print("=" * 80)
    search_asos_products("t-shirt")
