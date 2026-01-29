from fastapi import FastAPI, HTTPException, Query
from .models import Product, ProductCreate, ProductMetadataUpdate, SearchResponse
from .database import db
from .service import search_service
from .utils import generate_synthetic_data
from typing import Optional

app = FastAPI(
    title="E-commerce Search Engine",
    description="Search engine microservice for electronics",
    version="1.0.0"
)

# Bootstrap data on startup (mocking lifecycle event generally or just triggering it)
@app.on_event("startup")
async def startup_event():
    # If DB is empty, generate data
    if len(db.get_all_products()) == 0:
        generate_synthetic_data(1000)

@app.post("/api/v1/product", response_model=dict, status_code=201)
async def create_product(product: ProductCreate):
    new_product = db.add_product(product)
    return {"productId": new_product.productId}

@app.put("/api/v1/product/meta-data", response_model=Product)
async def update_metadata(payload: ProductMetadataUpdate):
    updated_product = db.update_metadata(payload.productId, payload.Metadata)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@app.get("/api/v1/search/product", response_model=SearchResponse)
async def search_products(query: str = Query(..., min_length=1)):
    results = search_service.search(query)
    return {"data": results}

@app.get("/api/v1/search/suggestions")
async def get_suggestions(query: str = Query(..., min_length=1)):
    return {"suggestions": search_service.get_suggestions(query)}

@app.get("/api/v1/product/trending", response_model=SearchResponse)
async def get_trending_products():
    return {"data": search_service.get_trending()}

@app.get("/api/v1/product/{product_id}/similar", response_model=SearchResponse)
async def get_similar(product_id: int):
    results = search_service.get_similar_products(product_id)
    return {"data": results}

@app.post("/api/v1/bootstrap")
async def bootstrap_data(count: int = 1000):
    generate_synthetic_data(count)
    return {"message": f"Generated {count} products"}

@app.get("/")
async def root():
    return {"message": "E-commerce Search Engine is running. Go to /docs for Swagger UI."}
