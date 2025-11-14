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
    line: str = Field(..., min_length=1, max_length=255, description="Số nhà, tòa nhà, tên đường")
    ward_id: str = Field(..., description="Phường/Xã")
    province_id: str = Field(..., description="Tỉnh/Thành phố")
    country: Optional[str] = Field(default="Việt Nam", max_length=100)

    @field_validator('line')
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
    line: Optional[str] = Field(None, min_length=1, max_length=255, description="Số nhà, tòa nhà, tên đường")
    ward_id: Optional[str] = Field(..., description="Phường/Xã")
    province_id: Optional[str] = Field(..., description="Tỉnh/Thành phố")
    country: Optional[str] = Field(None, max_length=100)

    @field_validator('line')
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
        if self.province_id is not None or self.ward_id is not None:
            if not all([self.province_id, self.ward_id]):
                raise ValueError(
                    'Nếu cập nhật địa chỉ, vui lòng cung cấp đầy đủ Province và Ward'
                )
        return self
