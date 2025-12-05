from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class BrandCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    logo: Optional[str] = None
    is_active: bool = True

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Tên của brand không được để trống')
        return v.strip()

    @field_validator('logo')
    @classmethod
    def validate_logo(cls, v):
        if v and len(str(v)) > 500:
            raise ValueError('Logo url quá dài')
        return v
    
class BrandUpdateModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    logo: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Tên của brand không được để trống')
        return v.strip()
    
class DeleteMultipleBrandsModel(BaseModel):
    brand_ids: List[str]