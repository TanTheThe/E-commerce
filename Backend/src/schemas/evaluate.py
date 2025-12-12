from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
import uuid


class EvaluateModel(BaseModel):
    id: uuid.UUID
    comment: Optional[str] = None
    rate: int
    image: Optional[str] = None
    product_id: uuid.UUID
    order_detail_id: uuid.UUID


class EvaluateInputModel(BaseModel):
    comment: Optional[str] = Field(None, max_length=1000, description="Nội dung đánh giá")
    rate: int = Field(..., ge=1, le=5, description="Số sao đánh giá (1-5)")
    image: Optional[str] = Field(None, description="URL hình ảnh đánh giá từ Supabase Storage")
    order_detail_id: str = Field(..., description="ID chi tiết đơn hàng")

    @field_validator('comment')
    @classmethod
    def validate_comment(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) < 10:
                raise ValueError("Nội dung đánh giá phải có ít nhất 10 ký tự")

        return v

    @field_validator('image')
    @classmethod
    def validate_image_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v = v.strip()
            if not v.startswith('https://'):
                raise ValueError("Image URL phải bắt đầu bằng https://")

            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
            if not any(v.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError("Image phải có định dạng: jpg, jpeg, png, webp hoặc gif")
            return v

        return None

class EvaluateCreateModel(BaseModel):
    comment: Optional[str] = None
    rate: int
    image: Optional[str] = None
    order_detail_id: str
    product_id: str
    product_variant_id: str
    user_id: str


class EvaluateFilterModel(BaseModel):
    search: Optional[str] = Field(None, max_length=255, description="Tìm kiếm theo tên khách hàng, sản phẩm, mã đơn")
    rate: Optional[int] = Field(None, ge=1, le=5, description="Lọc theo số sao (1-5)")
    sort_by_rate: Optional[Literal["highest", "lowest"]] = Field(None, description="Sắp xếp theo rating")
    sort_by_created_at: Optional[Literal["newest", "oldest"]] = Field(None, description="Sắp xếp theo thời gian")
    product_id: Optional[str] = Field(None, description="Lọc theo sản phẩm")
    user_id: Optional[str] = Field(None, description="Lọc theo người dùng")

    @field_validator('search')
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) < 2:
                raise ValueError("Từ khóa tìm kiếm phải có ít nhất 2 ký tự")
        return v

    @field_validator('sort_by_rate', 'sort_by_created_at')
    @classmethod
    def validate_sort(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if not v:
                return None
        return v


class SupplementEvaluateModel(BaseModel):
    additional_comment: Optional[str] = Field(None, min_length=1, max_length=1000)
    additional_image: Optional[str] = Field(None, max_length=500)

    @field_validator('additional_comment', 'additional_image')
    @classmethod
    def check_at_least_one_field(cls, v, values):
        if not v and not values.get('additional_comment') and not values.get('additional_image'):
            raise ValueError('Phải có ít nhất comment hoặc image')
        return v

    @field_validator('additional_image')
    @classmethod
    def validate_image_url(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL hình ảnh không hợp lệ')
        return v

class ReplyEvaluateModel(BaseModel):
    seller_reply: str = Field(..., min_length=1, max_length=1000)
