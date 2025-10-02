"""Database saver for scraped products"""

import os
import psycopg2
from psycopg2.extras import execute_values
import logging
from typing import List
from .models import ScrapedProduct

logger = logging.getLogger(__name__)


class DatabaseSaver:
    """Saves scraped products to PostgreSQL database"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

    def save_products(self, products: List[ScrapedProduct]) -> int:
        """
        Save products to database

        Returns:
            Number of products saved
        """
        if not products:
            logger.warning("No products to save")
            return 0

        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()

            saved_count = 0

            for product in products:
                # Get brand_id (or create if doesn't exist)
                cur.execute("SELECT id FROM brands WHERE name = %s", (product.brand,))
                row = cur.fetchone()
                if row:
                    brand_id = row[0]
                else:
                    cur.execute(
                        "INSERT INTO brands (name, slug) VALUES (%s, %s) RETURNING id",
                        (product.brand, product.brand.lower().replace(' ', '-'))
                    )
                    brand_id = cur.fetchone()[0]

                # Get store_id (or create if doesn't exist)
                cur.execute("SELECT id FROM stores WHERE name = %s", (product.store,))
                row = cur.fetchone()
                if row:
                    store_id = row[0]
                else:
                    cur.execute(
                        "INSERT INTO stores (name) VALUES (%s) RETURNING id",
                        (product.store,)
                    )
                    store_id = cur.fetchone()[0]

                # Insert or update product
                cur.execute("""
                    INSERT INTO products (
                        brand_id, store_id, external_id, name, description,
                        category, product_url, buy_url
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (store_id, external_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        category = EXCLUDED.category,
                        product_url = EXCLUDED.product_url,
                        buy_url = EXCLUDED.buy_url,
                        updated_at = NOW()
                    RETURNING id
                """, (
                    brand_id,
                    store_id,
                    product.external_id,
                    product.name,
                    product.description or "",
                    product.category,
                    product.product_url,
                    product.buy_url
                ))

                product_db_id = cur.fetchone()[0]

                # Insert images
                if product.images:
                    for idx, image_url in enumerate(product.images):
                        cur.execute("""
                            INSERT INTO product_images (product_id, src_url, position)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (product_db_id, image_url, idx))

                # Insert variants
                if product.variants:
                    for variant in product.variants:
                        cur.execute("""
                            INSERT INTO variants (
                                product_id, size, color, sku, price_cents, in_stock
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s
                            )
                            ON CONFLICT DO NOTHING
                        """, (
                            product_db_id,
                            variant.size,
                            variant.color,
                            variant.sku,
                            variant.price_cents,
                            variant.in_stock
                        ))

                saved_count += 1

            conn.commit()
            logger.info(f"✅ Saved {saved_count} products to database")
            return saved_count

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Error saving products to database: {e}")
            raise

        finally:
            if conn:
                cur.close()
                conn.close()

    def get_product_count(self) -> int:
        """Get total product count in database"""
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM products")
            count = cur.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"Error getting product count: {e}")
            return 0
        finally:
            if conn:
                cur.close()
                conn.close()
