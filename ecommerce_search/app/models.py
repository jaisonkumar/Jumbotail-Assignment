from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any

class ProductBase(BaseModel):
    title: str = Field(..., description="Name of the product")
    description: str = Field(..., description="Detailed description")
    mrp: float = Field(..., description="Maximum Retail Price")
    price: float = Field(..., description="Selling Price")
    currency: str = Field("Rupee", description="Currency code")
    stock: int = Field(..., description="Available stock")
    rating: float = Field(0.0, ge=0.0, le=5.0, description="Product rating")

class ProductCreate(ProductBase):
    pass

class ProductMetadataUpdate(BaseModel):
    productId: int
    Metadata: Dict[str, Any]

class Product(ProductBase):
    productId: int
    Metadata: Dict[str, Any] = {}
    sales_count: int = 0  # Internal metric for ranking
    recent_sales_count: int = 0 # Momentum signal
    return_rate: float = 0.0 # Negative signal (0.0 to 1.0)
    complaint_count: int = 0 # Negative signal
    
class SearchResponse(BaseModel):
    data: List[Product]
