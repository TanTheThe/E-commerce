from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator, field_validator


class StockStatus(str, Enum):
    DRAFT = "draft"                             # Mới tạo, chưa gửi
    SENT = "sent"                               # Đã gửi cho NCC
    CONFIRMED = "confirmed"                     # NCC đã xác nhận
    PARTIALLY_RECEIVED = "partially_received"   # Đã nhận một phần hàng
    COMPLETED = "completed"                     # Đã nhận đủ hàng
    CANCELLED = "cancelled"                     # Đơn bị hủy


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"                   # Chưa thanh toán.
    PARTIALLY_PAID = "partially_paid"   # Đã thanh toán một phần.
    PAID = "paid"                       # Thanh toán đủ.


class PurchaseOrderDetailCreate(BaseModel):
    product_variant_id: str = Field(description="ID của product variant")
    quantity: int = Field(gt=0, le=1000000, description="Số lượng đặt hàng")
    notes: Optional[str] = Field(None, max_length=1000, description="Ghi chú cho item này")

class CreatePurchaseOrderRequest(BaseModel):
    supplier_id: str = Field(description="ID nhà cung cấp")
    warehouse_id: str = Field(description="ID kho nhận hàng")
    notes: Optional[str] = Field(None, max_length=2000, description="Ghi chú chung cho PO")
    items: List[PurchaseOrderDetailCreate] = Field(
        min_length=1,
        max_length=500,
        description="Danh sách sản phẩm đặt hàng"
    )

    @model_validator(mode='after')
    def validate_unique_variants(self):
        variant_ids = [item.product_variant_id for item in self.items]
        if len(variant_ids) != len(set(variant_ids)):
            raise ValueError('Danh sách items chứa product_variant_id trùng lặp')
        return self




class ApprovePurchaseOrderRequest(BaseModel):
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Ghi chú khi duyệt (optional)"
    )


class SendPurchaseOrderRequest(BaseModel):
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Ghi chú khi gửi (optional)"
    )
    supplier_email: Optional[str] = Field(
        None,
        description="Email NCC (nếu khác với email mặc định)"
    )

    @field_validator('supplier_email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        v = v.strip()

        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, v):
            raise ValueError('Email không hợp lệ')

        if len(v) > 255:
            raise ValueError('Email quá dài (max 255 ký tự)')

        return v.lower()




class PurchaseOrderDetailUpdate(BaseModel):
    product_variant_id: str = Field(description="ID của product variant")
    quantity: int = Field(gt=0, le=1000000, description="Số lượng đặt hàng")
    notes: Optional[str] = Field(None, max_length=1000, description="Ghi chú cho item này")

class UpdatePurchaseOrderRequest(BaseModel):
    supplier_id: Optional[str] = Field(None, description="ID nhà cung cấp")
    warehouse_id: Optional[str] = Field(None, description="ID kho nhận hàng")
    notes: Optional[str] = Field(None, max_length=2000, description="Ghi chú")
    items: Optional[List[PurchaseOrderDetailCreate]] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Danh sách sản phẩm (nếu cập nhật)"
    )

    @model_validator(mode='after')
    def validate_at_least_one_field(self):
        if all(v is None for v in [self.supplier_id, self.warehouse_id, self.notes, self.items]):
            raise ValueError('Phải cập nhật ít nhất một trường')
        return self

    @model_validator(mode='after')
    def validate_unique_variants(self):
        if self.items:
            variant_ids = [item.product_variant_id for item in self.items]
            if len(variant_ids) != len(set(variant_ids)):
                raise ValueError('Danh sách items chứa product_variant_id trùng lặp')
        return self

class UpdatePurchaseOrderAfterNegotiationRequest(BaseModel):
    expected_delivery_date: Optional[datetime] = Field(
        None,
        description="Ngày giao hàng dự kiến sau thương lượng"
    )
    discount_amount: Optional[int] = Field(None, ge=0, le=2147483647, description="Số tiền giảm giá")
    shipping_cost: Optional[int] = Field(None, ge=0, le=2147483647, description="Phí vận chuyển")
    supplier_invoice_urls: List[str] = Field(
        min_length=1,
        max_length=10,
        description="Danh sách URLs bill/invoice từ NCC"
    )
    notes: Optional[str] = Field(None, max_length=2000, description="Ghi chú đơn hàng")
    items: Optional[List[PurchaseOrderDetailUpdate]] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Danh sách sản phẩm sau thương lượng"
    )

    @field_validator('expected_delivery_date')
    @classmethod
    def validate_delivery_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.date() < datetime.now().date():
            raise ValueError('Ngày giao hàng không được trong quá khứ')
        return v

    @model_validator(mode='after')
    def validate_unique_variants(self):
        if self.items:
            variant_ids = [item.product_variant_id for item in self.items]
            if len(variant_ids) != len(set(variant_ids)):
                raise ValueError('Danh sách items chứa product_variant_id trùng lặp')
        return self

