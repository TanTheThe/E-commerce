from typing import Optional
from pydantic import BaseModel, Field, model_validator, field_validator
import uuid

class AddressModel(BaseModel):
    id: uuid.UUID
    line: str
    street: str
    ward: str
    city: str
    district: str
    country: str = Field(default="Việt Nam")
    user_id: uuid.UUID


class AddressCreateModel(BaseModel):
    line: str = Field(..., min_length=1, max_length=255, description="Số nhà, tên đường")
    street: str = Field(..., min_length=1, max_length=100)
    ward: str = Field(..., min_length=1, max_length=100, description="Phường/Xã")
    district: str = Field(..., min_length=1, max_length=100, description="Quận/Huyện")
    city: str = Field(..., min_length=1, max_length=100, description="Tỉnh/Thành phố")
    country: Optional[str] = Field(default="Việt Nam", max_length=100)

    @field_validator('line', 'street', 'ward', 'district', 'city')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Trường này không được để trống hoặc chỉ chứa khoảng trắng')
        return v.strip()

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Tên quốc gia không hợp lệ')
        return v.strip()


class AddressUpdateModel(BaseModel):
    line: Optional[str] = Field(None, min_length=1, max_length=255)
    street: Optional[str] = Field(None, min_length=1, max_length=100)
    ward: Optional[str] = Field(None, min_length=1, max_length=100)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    district: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(default="Việt Nam", max_length=100)

    @field_validator('line', 'street', 'ward', 'district', 'city')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Trường này không được để trống hoặc chỉ chứa khoảng trắng')
        return v.strip()

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Tên quốc gia không hợp lệ')
        return v.strip()

    @model_validator(mode='after')
    def validate_address_completeness(self):
        address_fields_updated = any([
            self.city is not None,
            self.district is not None,
            self.ward is not None
        ])

        if address_fields_updated:
            if not all([self.city, self.district, self.ward]):
                raise ValueError(
                    'Nếu cập nhật địa chỉ, vui lòng cung cấp đầy đủ Tỉnh/Thành, Quận/Huyện và Phường/Xã'
                )

        return self
