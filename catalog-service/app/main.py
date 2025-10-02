from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ARRAY, TIMESTAMP
from datetime import datetime
import random

# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.fvpkhmtdvllnaazvlkah:AppleB4nanaxx@aws-1-eu-west-2.pooler.supabase.com:6543/postgres"
)

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Product model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(500), nullable=False)
    brand_name = Column(String(200), nullable=False)
    image_urls = Column(ARRAY(String), nullable=False)
    base_price = Column(Integer)
    currency = Column(String(3), default="USD")
    category = Column(String(100))
    product_url = Column(String(1000))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# FastAPI app
app = FastAPI(title="UPLO5 Catalog API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health_check():
    with Session(engine) as session:
        count = session.query(func.count(Product.id)).scalar()
        return {
            "status": "healthy",
            "database": "connected",
            "catalog_size": count,
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/api/v1/products/random")
def get_random_product():
    with Session(engine) as session:
        # Get total count
        count = session.query(func.count(Product.id)).scalar()

        if count == 0:
            return {"error": "No products in catalog"}

        # Random offset
        random_offset = random.randint(0, count - 1)

        # Fetch random product
        product = session.query(Product).offset(random_offset).limit(1).first()

        if not product:
            return {"error": "Product not found"}

        return {
            "id": product.id,
            "product_id": product.product_id,
            "name": product.name,
            "brand_name": product.brand_name,
            "image_urls": product.image_urls,
            "base_price": product.base_price,
            "currency": product.currency,
            "category": product.category,
            "product_url": product.product_url
        }

@app.get("/api/v1/products")
def list_products(skip: int = 0, limit: int = 20):
    with Session(engine) as session:
        products = session.query(Product).offset(skip).limit(limit).all()

        return [
            {
                "id": p.id,
                "product_id": p.product_id,
                "name": p.name,
                "brand_name": p.brand_name,
                "image_urls": p.image_urls,
                "base_price": p.base_price,
                "currency": p.currency,
                "category": p.category,
                "product_url": p.product_url
            }
            for p in products
        ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
