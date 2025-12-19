import re
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class SupplierProductCreate(BaseModel):
    product_id: str = Field(..., description="ID sản phẩm")
    is_active: bool = Field(default=True, description="Trạng thái hoạt động")
    notes: Optional[str] = Field(None, description="Ghi chú về sản phẩm này")

class SupplierCreate(BaseModel):
    name: str = Field(..., description="Tên nhà cung cấp", min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, description="Người liên hệ", max_length=255)
    phone: Optional[str] = Field(None, description="Số điện thoại", max_length=20)
    email: Optional[str] = Field(None, description="Email", max_length=255)
    address: Optional[str] = Field(None, description="Địa chỉ", max_length=500)
    bank_account: Optional[str] = Field(None, description="Số tài khoản ngân hàng", max_length=50)
    bank_name: Optional[str] = Field(None, description="Tên ngân hàng", max_length=255)
    credit_limit: Optional[int] = Field(None, description="Hạn mức công nợ", ge=0)
    notes: Optional[str] = Field(None, description="Ghi chú", max_length=1000)
    products: Optional[List[SupplierProductCreate]] = Field(
        default=[],
        description="Danh sách sản phẩm mà nhà cung cấp này cung cấp"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tên nhà cung cấp không được để trống")
        return v.strip()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None

        phone_cleaned = re.sub(r'[^\d+]', '', v.strip())
        if not re.match(r'^[\d+]{10,15}$', phone_cleaned):
            raise ValueError("Số điện thoại không hợp lệ (10-15 chữ số)")
        return phone_cleaned

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None

        email = v.strip().lower()
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError("Email không hợp lệ")
        return email

    @field_validator('bank_account')
    @classmethod
    def validate_bank_account(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None

        account = v.strip()
        if not re.match(r'^[\d]{6,20}$', account):
            raise ValueError("Số tài khoản ngân hàng không hợp lệ (6-20 chữ số)")
        return account

    @field_validator('products')
    @classmethod
    def validate_products_list(cls, v: Optional[List]) -> List:
        if v is None:
            return []

        if v:
            product_ids = [p.product_id for p in v]
            if len(product_ids) != len(set(product_ids)):
                raise ValueError("Danh sách sản phẩm có ID trùng lặp")

        return v

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

