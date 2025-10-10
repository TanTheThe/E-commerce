from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


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
    quantity: int = Field(gt=0, description="Số lượng đặt hàng")
    unit_cost: int = Field(gt=0, description="Giá mua một đơn vị (VND)")
    notes: Optional[str] = Field(None, description="Ghi chú cho item này")


class CreatePurchaseOrderRequest(BaseModel):
    supplier_id: str = Field(description="ID nhà cung cấp")
    warehouse_id: str = Field(description="ID kho nhận hàng")
    notes: Optional[str] = Field(None, description="Ghi chú chung cho PO")
    items: List[PurchaseOrderDetailCreate] = Field(min_length=1, description="Danh sách sản phẩm đặt hàng")


class UpdatePurchaseOrderRequest(BaseModel):
    supplier_id: Optional[str] = Field(None, description="ID nhà cung cấp")
    warehouse_id: Optional[str] = Field(None, description="ID kho nhận hàng")
    expected_delivery_date: Optional[datetime] = Field(None, description="Ngày dự kiến giao hàng")
    notes: Optional[str] = Field(None, description="Ghi chú")
    items: Optional[List[PurchaseOrderDetailCreate]] = Field(None, description="Danh sách sản phẩm (nếu cập nhật)")


class ApprovePurchaseOrderRequest(BaseModel):
    notes: Optional[str] = Field(None, description="Ghi chú khi duyệt (optional)")


class SendPurchaseOrderRequest(BaseModel):
    notes: Optional[str] = Field(None, description="Ghi chú khi gửi (optional)")
    supplier_email: Optional[str] = Field(None, description="Email NCC (nếu khác với email mặc định)")

