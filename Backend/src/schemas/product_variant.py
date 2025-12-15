from typing import Optional
from pydantic import BaseModel, Field, field_validator
import uuid


class ProductVariantCreateModel(BaseModel):
    size: Optional[str] = Field(None, max_length=50)
    color_id: Optional[str] = None
    color_name: Optional[str] = Field(None, max_length=100)
    color_code: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    image: str = Field(..., description="URL hình ảnh variant")
    price: int = Field(..., gt=0, description="Giá phải lớn hơn 0")
    quantity: int = Field(..., ge=0, description="Số lượng phải >= 0")
    sku: Optional[str] = Field(None, max_length=100)
    
    @field_validator('image')
    @classmethod
    def validate_image(cls, v):
        if not v.startswith('https://'):
            raise ValueError("Image URL phải bắt đầu bằng https://")

        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError("Image phải có định dạng: jpg, jpeg, png, webp hoặc gif")

        return v

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