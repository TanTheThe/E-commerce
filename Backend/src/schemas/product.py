from typing import Optional, List
from pydantic import BaseModel, Field
import uuid
from src.schemas.product_variant import ProductVariantModel, ProductVariantCreateModel, ProductVariantUpdateModel
from datetime import datetime
from enum import Enum


class ProductModel(BaseModel):
    id: uuid.UUID
    name: str
    images: List[str]
    description: Optional[str]
    status: str = Field(default="active")
    categories_id: List[uuid.UUID]
    product_variant: List[ProductVariantModel]


class ProductCreateModel(BaseModel):
    name: str
    images: List[str]
    description: Optional[str] = None
    categories_id: List[uuid.UUID]
    product_variant: List[ProductVariantCreateModel]

class ProductUpdateModel(BaseModel):
    name: str = None
    images: List[str] = None
    description: Optional[str] = None
    status: str = Field(default="active")
    categories_id: List[uuid.UUID] = None
    product_variant: List[ProductVariantUpdateModel] = None
    deleted_variant_ids: List[str] = None

class DeleteMultipleProductModel(BaseModel):
    product_ids: List[str]

class SortBy(str, Enum):
    newest = "newest"
    price_asc = "price_asc"
    price_desc = "price_desc"
    name_asc = "name_asc"
    name_desc = "name_desc"
    best_seller = "best_seller"
    sale_desc = "sale_desc"

class ProductFilterModel(BaseModel):
    search: Optional[str] = None
    category_ids: Optional[List[str]] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    sort_by: Optional[SortBy] = None
    colors: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    rating: Optional[List[int]] = None