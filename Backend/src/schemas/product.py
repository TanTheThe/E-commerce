from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid

from src.schemas.material import ProductMaterialCreateModel
from src.schemas.product_variant import ProductVariantCreateModel, ProductVariantUpdateModel
from datetime import datetime
from enum import Enum


class ProductCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Tên sản phẩm")
    images: List[str] = Field(..., min_items=1, max_items=10)
    description: Optional[str] = Field(None, max_length=5000)
    short_description: Optional[str] = Field(None, max_length=500)
    categories_id: List[str] = Field(..., min_items=1, max_items=10)
    product_variant: List[ProductVariantCreateModel] = Field(..., min_items=1)
    brand_id: Optional[str] = None
    materials: Optional[List[ProductMaterialCreateModel]] = Field(None, max_items=20)
    tags_id: Optional[List[str]] = Field(None, max_items=20)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Tên sản phẩm không được để trống")
        return ' '.join(v.split())
    
    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        for img in v:
            if not img.startswith('https://'):
                raise ValueError("Image URL phải bắt đầu bằng https://")
            if not any(img.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError("Image phải có định dạng: jpg, jpeg, png, webp hoặc gif")

        return v
    
    @field_validator('categories_id')
    @classmethod
    def validate_categories(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Danh sách categories có ID trùng lặp")
        return v
    
    @field_validator('tags_id')
    @classmethod
    def validate_tags(cls, v):
        if v and len(v) != len(set(v)):
            raise ValueError("Danh sách tags có ID trùng lặp")
        return v
    
    @field_validator('materials')
    @classmethod
    def validate_materials_percentage(cls, v):
        if v:
            total = sum(m.percentage for m in v)
            if total > 100:
                raise ValueError(f"Tổng phần trăm vật liệu vượt quá 100% (hiện tại: {total}%)")
            
            material_ids = [m.material_id for m in v]
            if len(material_ids) != len(set(material_ids)):
                raise ValueError("Có vật liệu bị trùng lặp")
        return v
    

class ProductUpdateModel(BaseModel):
    name: str = None
    images: List[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    status: str = Field(default="active")
    categories_id: List[uuid.UUID] = None
    brand_id: Optional[uuid.UUID] = None
    materials: Optional[List[dict]] = None
    tags_id: Optional[List[uuid.UUID]] = None
    product_variant: List[ProductVariantUpdateModel] = None
    deleted_variant_ids: List[str] = None

class DeleteMultipleProductModel(BaseModel):
    product_ids: List[str]

class SortBy(str, Enum):
    newest = "newest"
    oldest = "oldest"
    price_asc = "price_asc"
    price_desc = "price_desc"
    name_asc = "name_asc"
    name_desc = "name_desc"
    best_seller = "best_seller"
    sale_desc = "sale_desc"
    rating_desc = "rating_desc"

class ProductFilterModel(BaseModel):
    search: Optional[str] = Field(None, max_length=200, description="Tìm kiếm theo tên sản phẩm")
    category_ids: Optional[List[str]] = Field(default=None, max_items=20)
    category_slugs: Optional[List[str]] = Field(default=None, max_items=20)
    min_price: Optional[int] = Field(None, ge=0, description="Giá tối thiểu >= 0")
    max_price: Optional[int] = Field(None, ge=0, description="Giá tối đa >= 0")
    sort_by: Optional[SortBy] = None
    colors: Optional[List[str]] = Field(default=None, max_items=50)
    sizes: Optional[List[str]] = Field(default=None, max_items=20)
    rating: Optional[List[int]] = Field(default=None, max_items=5)
    brand_id: Optional[str] = None
    material_ids: Optional[List[str]] = Field(default=None, max_items=20)
    
    @field_validator('search')
    @classmethod
    def validate_search(cls, v):
        if v:
            cleaned = ' '.join(v.split())
            if len(cleaned) < 2:
                raise ValueError("Từ khóa tìm kiếm phải có ít nhất 2 ký tự")
            return cleaned
        return v
    
    @field_validator('min_price', 'max_price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError("Giá không được âm")
        return v
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v:
            for r in v:
                if r < 1 or r > 5:
                    raise ValueError("Rating phải từ 1-5")
        return v
    
    @field_validator('category_ids')
    @classmethod
    def validate_category_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Danh sách categories có ID trùng lặp")
        return v
    
    @field_validator('material_ids')
    @classmethod
    def validate_material_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Danh sách material_ids có ID trùng lặp")
        return v
    
    @field_validator('colors')
    @classmethod
    def validate_colors(cls, v):
        if v and len(v) != len(set(v)):
            raise ValueError("Danh sách colors có giá trị trùng lặp")
        return v
    
    @field_validator('sizes')
    @classmethod
    def validate_sizes(cls, v):
        if v and len(v) != len(set(v)):
            raise ValueError("Danh sách sizes có giá trị trùng lặp")
        return v
    
    @model_validator(mode='after')
    def validate_price_range(self):
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError("min_price không được lớn hơn max_price")
        return self
            

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class ProductStatusUpdateModel(BaseModel):
    status: ProductStatus

class BulkUpdateStatusModel(BaseModel):
    product_ids: List[str]
    status: ProductStatus