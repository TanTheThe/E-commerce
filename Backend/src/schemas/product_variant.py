from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


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
    id: Optional[str] = Field(None, description="ID của variant (nếu update variant có sẵn)")
    size: str = Field(..., min_length=1, max_length=50, description="Kích thước (S, M, L, XL, 38, 39, ...)")
    image: Optional[str] = Field(None, max_length=500, description="URL ảnh của variant")
    color_id: Optional[str] = Field(None, description="ID màu sắc từ bảng Color")
    color_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Tên màu (nếu không dùng color_id)")
    color_code: Optional[str] = Field(None, max_length=20, description="Mã màu hex (vd: #FF0000)")
    price: int = Field(..., ge=0, description="Giá bán (phải >= 0)")
    quantity: int = Field(..., ge=0, description="Số lượng tồn kho (phải >= 0)")
    sku: Optional[str] = Field(None, min_length=1, max_length=100, description="Mã SKU duy nhất")

    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        if v:
            v = v.strip().upper()
            if not v:
                raise ValueError('Kích thước không được để trống')
        return v

    @field_validator('image')
    @classmethod
    def validate_image_url(cls, v):
        if v:
            v = v.strip()
            if not v.startswith(('http://', 'https://', '/')):
                raise ValueError('URL ảnh không hợp lệ')

            valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
            if not any(v.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError(f'Ảnh phải có định dạng: {", ".join(valid_extensions)}')
        return v

    @field_validator('color_code')
    @classmethod
    def validate_color_code(cls, v):
        if v:
            v = v.strip()
            if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', v):
                raise ValueError('Mã màu phải theo format hex (#RRGGBB hoặc #RGB)')
        return v

    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v):
        if v:
            v = v.strip().upper()
            if not v:
                raise ValueError('SKU không được để trống')
        return v

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Giá không được âm')
        if v == 0:
            raise ValueError('Giá phải lớn hơn 0')
        if v > 999999999:
            raise ValueError('Giá không được vượt quá 999,999,999')
        return v

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Số lượng không được âm')
        if v > 999999:
            raise ValueError('Số lượng không được vượt quá 999,999')
        return v
