from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., description="Tên nhà cung cấp")
    contact_person: Optional[str] = Field(None, description="Người liên hệ")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    email: Optional[str] = Field(None, description="Email")
    address: Optional[str] = Field(None, description="Địa chỉ")
    bank_account: Optional[str] = Field(None, description="Số tài khoản ngân hàng")
    bank_name: Optional[str] = Field(None, description="Tên ngân hàng")
    credit_limit: Optional[int] = Field(None, description="Hạn mức công nợ")
    notes: Optional[str] = Field(None, description="Ghi chú")


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    credit_limit: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

