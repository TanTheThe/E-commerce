from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class SupplierProductCreate(BaseModel):
    product_id: str = Field(..., description="ID sản phẩm")
    is_active: bool = Field(default=True, description="Trạng thái hoạt động")
    notes: Optional[str] = Field(None, description="Ghi chú về sản phẩm này")

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

    products: Optional[List[SupplierProductCreate]] = Field(
        default=[],
        description="Danh sách sản phẩm mà nhà cung cấp này cung cấp"
    )

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
    product_ids: Optional[List[str]] = None
    add_products: Optional[List[SupplierProductCreate]] = None     # Thêm products
    remove_product_ids: Optional[List[str]] = None                 # Xóa products
    update_products: Optional[List[SupplierProductCreate]] = None  # Cập nhật is_active/notes

