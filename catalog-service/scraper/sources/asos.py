"""ASOS product scraper"""

from typing import List, Optional
from playwright.async_api import async_playwright
from .base import BaseScraper
from ..models import ScrapedProduct, ProductVariant
import logging
import asyncio
import json


logger = logging.getLogger(__name__)


class ASOSScraper(BaseScraper):
    """Scraper for ASOS products

    Note: ASOS uses Cloudflare bot protection. For production use, this scraper
    requires either:
    - Residential/mobile proxy rotation service
    - Cloudflare bypass tools (cloudscraper, FlareSolverr)
    - Commercial scraping API (ScraperAPI, ZenRows)

    Current implementation includes anti-detection measures but may still be blocked.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.brand = "ASOS"
        self.store = "ASOS"
        self.use_demo_mode = config.get('demo_mode', False)

    def _generate_demo_urls(self, url: str, count: int = 20) -> List[str]:
        """Generate demo product URLs for testing"""
        base_id = hash(url) % 10000000  # Deterministic IDs based on URL
        return [f"https://www.asos.com/us/product/prd/{base_id + i}" for i in range(count)]

    async def scrape_listing_page(self, url: str) -> List[str]:
        """
        Extract product URLs from ASOS listing page

        Args:
            url: ASOS category page URL

        Returns:
            List of product URLs
        """
        # Demo mode for testing without hitting ASOS servers
        if self.use_demo_mode:
            logger.info(f"Demo mode: Generating sample URLs for {url}")
            return self._generate_demo_urls(url, 20)

        product_urls = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            try:
                # Add extra stealth measures
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

                await page.goto(url, wait_until='load', timeout=60000)

                # Wait extra time for JavaScript to load
                await asyncio.sleep(5)

                # Rate limiting - 2 seconds between requests
                await asyncio.sleep(2)

                # Extract product links using multiple selector strategies
                links = await page.evaluate("""() => {
                    const productLinks = new Set();

                    // Strategy 1: Look for product tile articles with links
                    const tiles = document.querySelectorAll('article[data-auto-id="productTile"] a, article a[href*="/prd/"]');
                    tiles.forEach(link => {
                        const href = link.getAttribute('href');
                        if (href && href.includes('/prd/')) {
                            const fullUrl = href.startsWith('http') ? href : 'https://www.asos.com' + href;
                            productLinks.add(fullUrl);
                        }
                    });

                    // Strategy 2: Look for any links containing /prd/
                    const prdLinks = document.querySelectorAll('a[href*="/prd/"]');
                    prdLinks.forEach(link => {
                        const href = link.getAttribute('href');
                        if (href) {
                            const fullUrl = href.startsWith('http') ? href : 'https://www.asos.com' + href;
                            productLinks.add(fullUrl);
                        }
                    });

                    // Strategy 3: Look for section elements with data-id attribute
                    const sections = document.querySelectorAll('section[data-id] a');
                    sections.forEach(link => {
                        const href = link.getAttribute('href');
                        if (href && href.includes('/prd/')) {
                            const fullUrl = href.startsWith('http') ? href : 'https://www.asos.com' + href;
                            productLinks.add(fullUrl);
                        }
                    });

                    return Array.from(productLinks);
                }""")

                product_urls = list(set(links))  # Remove duplicates
                logger.info(f"Found {len(product_urls)} unique product URLs from ASOS listing")

            except Exception as e:
                logger.error(f"Error scraping ASOS listing page: {e}")

            finally:
                await browser.close()

        return product_urls

    async def scrape_product_detail(self, url: str) -> Optional[ScrapedProduct]:
        """
        Extract product details from ASOS product page with retry logic

        Args:
            url: ASOS product page URL

        Returns:
            ScrapedProduct or None if scraping failed
        """
        max_retries = 3

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries} after {wait_time}s delay")
                    await asyncio.sleep(wait_time)

                product = await self._scrape_product_once(url)
                if product:
                    return product

            except Exception as e:
                logger.error(f"Error scraping ASOS product {url} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None

        return None

    def _generate_demo_product(self, url: str) -> ScrapedProduct:
        """Generate a demo ASOS product for testing"""
        import random

        product_id = url.split('/')[-1]
        hash_val = hash(url)

        # Sample product names
        names = [
            "ASOS DESIGN slim fit t-shirt with crew neck",
            "ASOS DESIGN oversized t-shirt in washed black",
            "ASOS DESIGN midi dress with v neck",
            "ASOS DESIGN jersey maxi dress in floral",
            "ASOS DESIGN skinny jeans in mid wash blue",
            "ASOS DESIGN slim jeans with rips in black",
            "ASOS DESIGN cropped t-shirt in white",
            "ASOS DESIGN longline t-shirt with curved hem"
        ]
        name = names[hash_val % len(names)]

        # Sample descriptions
        descriptions = [
            "Made from soft cotton jersey fabric. Regular fit. Crew neckline. Short sleeves.",
            "Relaxed oversized fit. Soft washed finish. Round neckline.",
            "Woven fabric. V-neckline. Sleeveless design. Midi length.",
            "Jersey material. Maxi length. Pull-on design. Floral print."
        ]
        description = descriptions[hash_val % len(descriptions)]

        price = round(15 + (hash_val % 50) + ((hash_val % 100) / 100), 2)

        # Generate sample images
        img_ids = [1234 + (hash_val + i) % 9999 for i in range(4)]
        images = [f"https://images.asos-media.com/products/{img_id}/1-1.jpg" for img_id in img_ids]

        # Generate sizes
        size_options = ["XS", "S", "M", "L", "XL", "XXL"]
        variants = [
            ProductVariant(
                size=size,
                price_cents=int(price * 100),
                in_stock=(hash_val + i) % 3 != 0  # Some sizes out of stock
            )
            for i, size in enumerate(size_options)
        ]

        # Determine category from URL
        category = 'other'
        if 't-shirt' in url or 't-shirts' in url or 'tops' in url:
            category = 'mens-tops' if 'men' in url else 'womens-tops'
        elif 'dress' in url:
            category = 'dresses'
        elif 'jeans' in url:
            category = 'mens-bottoms' if 'men' in url else 'womens-bottoms'

        return ScrapedProduct(
            external_id=product_id,
            name=name,
            description=description,
            category=category,
            brand=self.brand,
            store=self.store,
            product_url=url,
            buy_url=url,
            images=images,
            variants=variants
        )

    async def _scrape_product_once(self, url: str) -> Optional[ScrapedProduct]:
        """
        Single attempt to scrape product details from ASOS product page

        Args:
            url: ASOS product page URL

        Returns:
            ScrapedProduct or None if scraping failed
        """
        # Demo mode for testing without hitting ASOS servers
        if self.use_demo_mode:
            logger.info(f"Demo mode: Generating sample product for {url}")
            await asyncio.sleep(0.5)  # Simulate network delay
            return self._generate_demo_product(url)

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            try:
                # Add extra stealth measures
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

                await page.goto(url, wait_until='domcontentloaded', timeout=60000)

                # Rate limiting - 2 seconds between requests
                await asyncio.sleep(2)

                # Wait for product content to load - more flexible
                try:
                    await page.wait_for_selector('h1, div[class*="product"], script[type="application/ld+json"]', timeout=20000)
                except:
                    # If specific selectors fail, just wait a bit and try to extract anyway
                    await asyncio.sleep(3)

                # Try to extract JSON-LD structured data first
                json_ld_data = await page.evaluate("""() => {
                    const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                    for (const script of scripts) {
                        try {
                            const data = JSON.parse(script.textContent);
                            if (data['@type'] === 'Product' || (data['@graph'] && data['@graph'].find(item => item['@type'] === 'Product'))) {
                                return script.textContent;
                            }
                        } catch (e) {
                            continue;
                        }
                    }
                    return null;
                }""")

                # Extract product data using multiple strategies
                data = await page.evaluate("""() => {
                    // Strategy 1: Extract from JSON-LD if available
                    let jsonLdProduct = null;
                    const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                    for (const script of scripts) {
                        try {
                            const data = JSON.parse(script.textContent);
                            if (data['@type'] === 'Product') {
                                jsonLdProduct = data;
                                break;
                            } else if (data['@graph']) {
                                const product = data['@graph'].find(item => item['@type'] === 'Product');
                                if (product) {
                                    jsonLdProduct = product;
                                    break;
                                }
                            }
                        } catch (e) {
                            continue;
                        }
                    }

                    // Strategy 2: Extract from HTML elements
                    // Product name
                    const nameSelectors = [
                        'h1',
                        '[class*="product-hero"] h1',
                        '[data-test-id="product-name"]',
                        'h1[class*="name"]',
                        'h1[class*="title"]'
                    ];
                    let name = '';
                    for (const selector of nameSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.textContent.trim()) {
                            name = el.textContent.trim();
                            break;
                        }
                    }
                    if (jsonLdProduct && jsonLdProduct.name) {
                        name = jsonLdProduct.name;
                    }

                    // Product description
                    const descSelectors = [
                        '[class*="product-description"]',
                        '[data-test-id="product-description"]',
                        'div[class*="description"]',
                        'div[class*="details"]'
                    ];
                    let description = '';
                    for (const selector of descSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.textContent.trim()) {
                            description = el.textContent.trim();
                            break;
                        }
                    }
                    if (jsonLdProduct && jsonLdProduct.description) {
                        description = jsonLdProduct.description;
                    }

                    // Product price
                    const priceSelectors = [
                        '[data-testid="current-price"]',
                        '[class*="current-price"]',
                        'span[data-id="current-price"]',
                        '[class*="price"]',
                        'span[class*="price"]'
                    ];
                    let priceText = '0';
                    for (const selector of priceSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.textContent.trim()) {
                            priceText = el.textContent.trim();
                            break;
                        }
                    }
                    if (jsonLdProduct && jsonLdProduct.offers && jsonLdProduct.offers.price) {
                        priceText = jsonLdProduct.offers.price.toString();
                    }
                    const priceMatch = priceText.replace(/[^0-9.]/g, '');
                    const price = priceMatch ? parseFloat(priceMatch) : 0;

                    // Product images
                    let images = [];
                    if (jsonLdProduct && jsonLdProduct.image) {
                        images = Array.isArray(jsonLdProduct.image) ? jsonLdProduct.image : [jsonLdProduct.image];
                    } else {
                        const imgSelectors = [
                            'img[class*="product-image"]',
                            'img[class*="gallery"]',
                            'button[class*="thumbnail"] img',
                            'img[src*="asos-media"]',
                            'img[src*="images.asos"]'
                        ];
                        const imgElements = [];
                        for (const selector of imgSelectors) {
                            const elements = document.querySelectorAll(selector);
                            imgElements.push(...Array.from(elements));
                        }
                        images = Array.from(new Set(
                            imgElements
                                .map(img => img.getAttribute('src') || img.getAttribute('data-src'))
                                .filter(src => src && src.startsWith('http') && !src.includes('placeholder'))
                        )).slice(0, 5);
                    }

                    // Product ID from URL
                    const productIdMatch = window.location.href.match(/prd\\/([0-9]+)/);
                    const productId = productIdMatch ? productIdMatch[1] : Date.now().toString();

                    // Available sizes
                    const sizeSelectors = [
                        'select[data-id="sizeSelect"] option',
                        'button[class*="size"]',
                        'select[id*="size"] option',
                        'button[data-id*="size"]'
                    ];
                    let sizes = [];
                    for (const selector of sizeSelectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            sizes = Array.from(elements).map(el => {
                                let sizeText = el.textContent.trim();
                                // For select options, use value or text
                                if (el.tagName === 'OPTION') {
                                    sizeText = el.value || el.textContent.trim();
                                    if (sizeText === '' || sizeText === 'Please select') return null;
                                }
                                const available = !el.hasAttribute('disabled') &&
                                                !el.classList.contains('disabled') &&
                                                !el.classList.contains('out-of-stock');
                                return sizeText ? { size: sizeText, available } : null;
                            }).filter(s => s !== null);
                            if (sizes.length > 0) break;
                        }
                    }

                    // Color variants
                    const colorSelectors = [
                        'button[class*="colour"]',
                        'button[class*="color"]',
                        'select[id*="colour"] option',
                        'img[alt*="colour"]'
                    ];
                    let colors = [];
                    for (const selector of colorSelectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            colors = Array.from(elements)
                                .map(el => {
                                    const colorText = el.getAttribute('aria-label') ||
                                                    el.getAttribute('title') ||
                                                    el.textContent.trim();
                                    return colorText;
                                })
                                .filter(c => c && c.length > 0 && c !== 'Please select')
                                .slice(0, 10);
                            if (colors.length > 0) break;
                        }
                    }

                    return {
                        name,
                        description,
                        price,
                        images,
                        productId,
                        sizes,
                        colors
                    };
                }""")

                # Validate extracted data
                if not data.get('name') or data.get('price') == 0 or len(data.get('images', [])) < 2:
                    logger.warning(f"Incomplete data for ASOS product {url}: name={bool(data.get('name'))}, price={data.get('price')}, images={len(data.get('images', []))}")
                    await browser.close()
                    return None

                # Create product variants
                variants = []
                if data.get('sizes') and len(data['sizes']) > 0:
                    for size_info in data['sizes']:
                        variants.append(ProductVariant(
                            size=size_info['size'],
                            price_cents=int(data['price'] * 100),
                            in_stock=size_info['available']
                        ))
                else:
                    # Default variant if no sizes found
                    variants.append(ProductVariant(
                        price_cents=int(data['price'] * 100),
                        in_stock=True
                    ))

                # Determine category from URL
                category = 'other'
                url_lower = url.lower()
                if '/men/' in url_lower or '/mens-' in url_lower:
                    category = 'mens'
                elif '/women/' in url_lower or '/womens-' in url_lower:
                    category = 'womens'

                if 't-shirt' in url_lower or 'tops' in url_lower or 'tshirt' in url_lower:
                    category += '-tops'
                elif 'dress' in url_lower:
                    category = 'dresses'
                elif 'jeans' in url_lower or 'pants' in url_lower or 'trousers' in url_lower:
                    category += '-bottoms'
                elif 'jacket' in url_lower or 'coat' in url_lower:
                    category += '-outerwear'
                elif 'shoe' in url_lower or 'sneaker' in url_lower:
                    category += '-shoes'

                # Create ScrapedProduct
                product = ScrapedProduct(
                    external_id=data['productId'],
                    name=data['name'],
                    description=data.get('description', ''),
                    category=category,
                    brand=self.brand,
                    store=self.store,
                    product_url=url,
                    buy_url=url,
                    images=data['images'],
                    variants=variants
                )

                await browser.close()
                logger.info(f"Successfully scraped ASOS product: {data['name']}")
                return product

            except Exception as e:
                logger.error(f"Error scraping ASOS product {url}: {e}")
                await browser.close()
                return None


# Default configuration for ASOS scraper
ASOS_CONFIG = {
    'brand': 'ASOS',
    'store': 'ASOS',
    'urls': [
        # Men's Categories
        'https://www.asos.com/us/men/t-shirts-tank-tops/cat/?cid=7616',
        'https://www.asos.com/us/men/jeans/cat/?cid=4208',
        'https://www.asos.com/us/men/shirts/cat/?cid=3602',
        'https://www.asos.com/us/men/pants/cat/?cid=4910',
        'https://www.asos.com/us/men/hoodies-sweatshirts/cat/?cid=5668',

        # Women's Categories
        'https://www.asos.com/us/women/dresses/cat/?cid=8799',
        'https://www.asos.com/us/women/tops/cat/?cid=4169',
        'https://www.asos.com/us/women/jeans/cat/?cid=2639',
        'https://www.asos.com/us/women/pants/cat/?cid=2640',
        'https://www.asos.com/us/women/coats-jackets/cat/?cid=2641',
    ],
    'rate_limit': '1/2s',  # 1 request per 2 seconds
    'max_products': 500,
    'demo_mode': True  # 🧪 DEMO MODE - Generate sample products for testing
}

# IMPORTANT: ASOS uses Cloudflare bot protection
# For production deployment, consider:
# 1. Using residential proxy rotation (recommended)
# 2. Implementing cloudscraper or FlareSolverr
# 3. Using commercial scraping API (ScraperAPI, ZenRows)
# 4. Respecting robots.txt and rate limits
