from pydantic import BaseModel, field_validator
from sqlmodel import Field
import re


class PaymentRequest(BaseModel):
    order_type: str = Field(..., min_length=1, max_length=50)
    order_code: str = Field(..., min_length=1, max_length=100)
    amount: int = Field(..., ge=5000, le=1000000000)
    order_desc: str = Field(..., min_length=1, max_length=500)
    bank_code: str = Field(default="", max_length=20)
    language: str = Field(default="vn", max_length=5)

    @field_validator('order_code')
    @classmethod
    def validate_order_code(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Mã đơn hàng chỉ được chứa chữ cái, số, gạch dưới và gạch ngang')
        return v

    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        if v and v not in ['vn', 'en']:
            raise ValueError('Ngôn ngữ chỉ hỗ trợ "vn" hoặc "en"')
        return v or 'vn'

    @field_validator('bank_code')
    @classmethod
    def validate_bank_code(cls, v):
        if v and not re.match(r'^[A-Z0-9]+$', v):
            raise ValueError('Mã ngân hàng không hợp lệ')
        return v


class PaymentStatusType:
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"