import re
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator, model_validator


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
    
    
class SupplierProductUpdate(BaseModel):
    product_id: str = Field(..., description="ID sản phẩm")
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động")
    notes: Optional[str] = Field(None, description="Ghi chú", max_length=1000)

class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Tên nhà cung cấp", min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, description="Người liên hệ", max_length=255)
    phone: Optional[str] = Field(None, description="Số điện thoại", max_length=20)
    email: Optional[str] = Field(None, description="Email", max_length=255)
    address: Optional[str] = Field(None, description="Địa chỉ", max_length=500)
    bank_account: Optional[str] = Field(None, description="Số tài khoản", max_length=50)
    bank_name: Optional[str] = Field(None, description="Tên ngân hàng", max_length=255)
    credit_limit: Optional[int] = Field(None, description="Hạn mức công nợ", ge=0)
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động")
    notes: Optional[str] = Field(None, description="Ghi chú", max_length=1000)
    
    add_products: Optional[List[SupplierProductUpdate]] = Field(
        default=None,
        description="Thêm sản phẩm mới"
    )
    remove_product_ids: Optional[List[str]] = Field(
        default=None,
        description="Xóa sản phẩm theo ID"
    )
    update_products: Optional[List[SupplierProductUpdate]] = Field(
        default=None,
        description="Cập nhật thông tin sản phẩm"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Tên nhà cung cấp không được để trống")
        return v

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
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Email không hợp lệ")
        return email
    
    @field_validator('bank_account')
    @classmethod
    def validate_bank_account(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        account = v.strip()
        if not re.match(r'^[\d]{6,20}$', account):
            raise ValueError("Số tài khoản không hợp lệ (6-20 chữ số)")
        return account
    
    @field_validator('add_products', 'remove_product_ids', 'update_products')
    @classmethod
    def validate_product_lists(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v
    
    @model_validator(mode='after')
    def validate_product_operations(self):
        add_ids = {p.product_id for p in self.add_products} if self.add_products else set()
        remove_ids = set(self.remove_product_ids) if self.remove_product_ids else set()
        update_ids = {p.product_id for p in self.update_products} if self.update_products else set()

        if self.add_products and len(add_ids) != len(self.add_products):
            raise ValueError("Danh sách add_products có ID trùng lặp")

        if self.update_products and len(update_ids) != len(self.update_products):
            raise ValueError("Danh sách update_products có ID trùng lặp")

        if self.remove_product_ids and len(remove_ids) != len(self.remove_product_ids):
            raise ValueError("Danh sách remove_product_ids có ID trùng lặp")

        conflict_add_remove = add_ids & remove_ids
        if conflict_add_remove:
            raise ValueError(
                f"Sản phẩm {conflict_add_remove} không thể vừa thêm vừa xóa"
            )

        conflict_add_update = add_ids & update_ids
        if conflict_add_update:
            raise ValueError(
                f"Sản phẩm {conflict_add_update} không thể vừa thêm vừa cập nhật"
            )

        conflict_remove_update = remove_ids & update_ids
        if conflict_remove_update:
            raise ValueError(
                f"Sản phẩm {conflict_remove_update} không thể vừa xóa vừa cập nhật"
            )

        return self
    
    
    

