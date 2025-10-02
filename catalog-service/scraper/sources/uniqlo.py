"""
UNIQLO Product Scraper
Successfully fetches real product data with images from UNIQLO's public API
"""
import requests
from typing import List, Optional
import logging
from .base import BaseScraper
from ..models import ScrapedProduct, ProductVariant

logger = logging.getLogger(__name__)


class UniqloScraper(BaseScraper):
    """Scraper for UNIQLO products using their public API"""

    BASE_URL = "https://www.uniqlo.com/us/api/commerce/v5/en/products"

    SEARCH_QUERIES = [
        "shirt", "t-shirt", "jeans", "pants", "dress", "sweater",
        "hoodie", "jacket", "coat", "blazer", "skirt", "shorts"
    ]

    def __init__(self, config: dict):
        super().__init__(config)
        self.brand = "UNIQLO"
        self.store = "UNIQLO"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
        })

    async def scrape_listing_page(self, query: str) -> List[str]:
        """
        Search for products by query using UNIQLO API

        Args:
            query: Search query (e.g., "jeans", "shirt")

        Returns:
            List of product IDs (we'll use IDs as URLs for the detail method)
        """
        try:
            params = {
                'q': query,
                'limit': 50,
                'offset': 0,
            }

            response = self.session.get(self.BASE_URL, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                items = data.get('result', {}).get('items', [])
                product_ids = [item.get('productId', '') for item in items if item.get('productId')]
                logger.info(f"Found {len(product_ids)} products for query '{query}'")
                return product_ids
            else:
                logger.error(f"API request failed: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")
            return []

    async def scrape_product_detail(self, product_id: str) -> Optional[ScrapedProduct]:
        """
        We don't actually fetch individual products - we already have all the data
        from the listing page. This is called with the full item dict as JSON.

        For simplicity, we'll re-fetch the product from the API.
        """
        try:
            # Search for this specific product ID
            params = {'q': product_id, 'limit': 1}
            response = self.session.get(self.BASE_URL, params=params, timeout=15)

            if response.status_code != 200:
                return None

            data = response.json()
            items = data.get('result', {}).get('items', [])

            if not items:
                return None

            item = items[0]
            return self._transform_product(item)

        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None

    async def scrape_all(self, limit: Optional[int] = None) -> List[ScrapedProduct]:
        """
        Main scraping method - searches across multiple queries

        Args:
            limit: Maximum products to scrape

        Returns:
            List of ScrapedProduct objects
        """
        max_to_scrape = limit if limit is not None else self.max_products
        logger.info(f"Starting UNIQLO scrape (limit: {max_to_scrape})")

        all_products = []
        seen_ids = set()

        # Search across different product types
        products_per_query = max(10, max_to_scrape // len(self.SEARCH_QUERIES))

        for query in self.SEARCH_QUERIES:
            if len(all_products) >= max_to_scrape:
                break

            logger.info(f"Searching for: {query}")

            try:
                params = {
                    'q': query,
                    'limit': products_per_query,
                    'offset': 0,
                }

                response = self.session.get(self.BASE_URL, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    items = data.get('result', {}).get('items', [])
                    logger.info(f"Found {len(items)} products for query '{query}'")

                    for item in items:
                        product_id = item.get('productId', '')

                        # Skip duplicates
                        if product_id in seen_ids:
                            continue

                        seen_ids.add(product_id)

                        # Transform to ScrapedProduct
                        product = self._transform_product(item)
                        if product:
                            all_products.append(product)

                        if len(all_products) >= max_to_scrape:
                            break

            except Exception as e:
                logger.error(f"Error searching for '{query}': {e}")
                continue

        logger.info(f"Successfully scraped {len(all_products)} UNIQLO products")
        return all_products

    def _transform_product(self, item: dict) -> Optional[ScrapedProduct]:
        """Transform UNIQLO API response to ScrapedProduct format"""
        try:
            # Extract basic info
            product_id = item.get('productId', '')
            name = item.get('name', 'Unknown Product')

            # Get price (in cents)
            prices = item.get('prices', {})
            base_price = prices.get('base', {})
            price_value = base_price.get('value', 0)
            price_cents = int(price_value * 100)  # Convert dollars to cents

            # Get images - UNIQLO has complex nested structure
            images_data = item.get('images', {})
            image_urls = []

            # Get main images (one per color)
            main_images = images_data.get('main', {})
            for color_code, img_data in main_images.items():
                if isinstance(img_data, dict) and 'image' in img_data:
                    img_url = img_data['image']
                    if img_url and img_url not in image_urls:
                        # Upgrade to larger size for better quality
                        large_url = img_url.replace('_3x4.jpg', '_zoom.jpg')
                        image_urls.append(large_url)

            # Get sub/additional images
            sub_images = images_data.get('sub', [])
            for img_data in sub_images:
                if isinstance(img_data, dict) and 'image' in img_data:
                    img_url = img_data['image']
                    if img_url and img_url not in image_urls:
                        large_url = img_url.replace('_3x4.jpg', '_zoom.jpg')
                        image_urls.append(large_url)

            # Get colors
            colors = []
            for color_data in item.get('colors', []):
                color_name = color_data.get('name', '')
                if color_name:
                    colors.append(color_name)

            # Get sizes
            sizes = []
            for size_data in item.get('sizes', []):
                size_name = size_data.get('name', '')
                if size_name:
                    sizes.append(size_name)

            # Category/tags
            category = item.get('category', {}).get('name', 'other')

            # Stock status
            in_stock = item.get('stock', {}).get('statusText', '').lower() != 'out of stock'

            # Product URL
            product_url = f"https://www.uniqlo.com/us/en/products/{product_id}"

            # Description (if available)
            description = item.get('longDescription', item.get('shortDescription', name))

            # Create variants (one for each color/size combination)
            variants = []
            if colors and sizes:
                # Create a variant for each color/size combo
                for color in colors[:3]:  # Limit to 3 colors to avoid explosion
                    for size in sizes[:5]:  # Limit to 5 sizes
                        variants.append(ProductVariant(
                            color=color,
                            size=size,
                            sku=f"UNIQLO-{product_id}-{color[:3]}-{size}",
                            price_cents=price_cents,
                            in_stock=in_stock
                        ))
            else:
                # Create a single default variant
                variants.append(ProductVariant(
                    color=colors[0] if colors else None,
                    size=sizes[0] if sizes else None,
                    sku=f"UNIQLO-{product_id}",
                    price_cents=price_cents,
                    in_stock=in_stock
                ))

            return ScrapedProduct(
                external_id=product_id,
                name=name,
                description=description,
                category=category.lower(),
                brand='UNIQLO',
                store='UNIQLO',
                product_url=product_url,
                buy_url=product_url,
                images=image_urls[:5],  # Limit to 5 images
                variants=variants
            )

        except Exception as e:
            logger.error(f"Error transforming product: {e}")
            return None


# Config for UNIQLO scraper
UNIQLO_CONFIG = {
    'brand': 'UNIQLO',
    'store': 'UNIQLO',
    'urls': ['shirt', 't-shirt', 'jeans'],  # Search queries instead of URLs
    'max_products': 500,
    'rate_limit': '1/1s',
}
