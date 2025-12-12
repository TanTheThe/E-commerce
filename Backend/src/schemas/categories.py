from pydantic import BaseModel, Field, field_validator
import uuid
from typing import Optional

class CategoriesModel(BaseModel):
    id: uuid.UUID
    name: str
    images: str


class CategoriesCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Tên danh mục")
    image: str = Field(..., min_length=1, description="URL hình ảnh")
    parent_id: Optional[str] = Field(None, description="ID danh mục cha")
    type_size: str = Field(..., min_length=1, description="Loại size")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Tên danh mục không được để trống hoặc chỉ có khoảng trắng")
        return v.strip()

    @field_validator('image')
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        if not v.startswith('https://'):
            raise ValueError("Image URL phải bắt đầu bằng https://")

        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError("Image phải có định dạng: jpg, jpeg, png, webp hoặc gif")

        return v

class CategoryUpdateModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên danh mục")
    image: Optional[str] = Field(None, description="URL hình ảnh từ Supabase Storage")
    parent_id: Optional[str] = Field(None, description="ID danh mục cha")
    type_size: Optional[str] = Field(None, min_length=1, max_length=50, description="Loại size")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Tên danh mục không được để trống hoặc chỉ có khoảng trắng")
        return v

    @field_validator('image')
    @classmethod
    def validate_image_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.startswith('https://'):
                raise ValueError("Image URL phải bắt đầu bằng https://")

            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
            if not any(v.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError("Image phải có định dạng: jpg, jpeg, png, webp hoặc gif")
        return v

    @field_validator('type_size')
    @classmethod
    def validate_type_size(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Loại size không được để trống")
        return v


class CategoriesFilterModel(BaseModel):
    search: Optional[str] = Field(None, max_length=255, description="Tìm kiếm theo tên")
    parent_id: Optional[str] = Field(None, description="Lọc theo danh mục cha")
    type_size: Optional[str] = Field(None, max_length=50, description="Lọc theo loại size")

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

    @field_validator('type_size')
    @classmethod
    def validate_type_size(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v