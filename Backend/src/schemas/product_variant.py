from typing import Optional
from pydantic import BaseModel
import uuid


class ProductVariantModel(BaseModel):
    id: uuid.UUID
    size: Optional[str]
    color: Optional[str]
    price: int
    quantity: int
    sku: str
    product_id: uuid.UUID


class ProductVariantCreateModel(BaseModel):
    size: Optional[str] = None
    color_id: Optional[str] = None
    color_name: Optional[str] = None
    color_code: Optional[str] = None
    image: str
    price: int
    quantity: int
    sku: Optional[str] = None

class ProductVariantUpdateModel(BaseModel):
    id: Optional[str] = None
    size: Optional[str] = None
    image: Optional[str] = None
    color_id: Optional[str] = None
    color_name: Optional[str] = None
    color_code: Optional[str] = None
    price: int
    quantity: int
    sku: Optional[str] = None