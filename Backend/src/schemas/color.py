from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid


class Color(BaseModel):
    id: uuid.UUID
    name: str

class ColorCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Tên màu không được để trống')
        return v.strip()

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Mã màu không được để trống')
        return v.strip()


class ColorUpdateModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=50)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Tên màu không được để trống')
        return v.strip()

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Mã màu không được để trống')
        return v.strip()

class ColorFilterModel(BaseModel):
    search: Optional[str] = Field(None, max_length=200)
