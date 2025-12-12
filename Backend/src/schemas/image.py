from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class UploadType(str, Enum):
    BRANDS = "brands"
    CATEGORIES = "categories"
    PRODUCTS = "products"


class ImageUploadModel(BaseModel):
    type: UploadType = Field(..., description="Loại upload: brands, categories, products")
    slug: str = Field(..., min_length=1, max_length=255, description="Slug để đặt tên file")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if not v.strip():
            raise ValueError('Slug không được để trống')

        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug chỉ được chứa chữ, số, dấu gạch ngang và gạch dưới')
        return v.strip().lower()


class ImageDeleteModel(BaseModel):
    file_path: str = Field(..., min_length=1, max_length=500)

    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v):
        if not v.strip():
            raise ValueError('File path không được để trống')

        allowed_prefixes = ['brands/', 'categories/', 'products/']
        if not any(v.startswith(prefix) for prefix in allowed_prefixes):
            raise ValueError('File path không hợp lệ')
        return v.strip()