from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class GoodsReceiptStatus(str, Enum):
    PENDING = "pending"               # Mới tạo, chờ xác nhận nhận hàng
    INSPECTING = "inspecting"         # Đang kiểm hàng
    APPROVED = "approved"             # Đã kiểm và duyệt
    REJECTED = "rejected"             # Bị từ chối (hàng lỗi, sai khác...).
    COMPLETED = "completed"           # Hoàn tất nhập kho

class QualityStatus(str, Enum):
    PENDING = "pending"   # chưa kiểm hàng
    PASS = "pass"         # đạt chất lượng
    FAIL = "fail"         # không đạt
    PARTIAL = "partial"   # đạt một phần (một phần bị loại)

class GoodsReceiptDetailCreate(BaseModel):
    po_detail_id: str = Field(description="ID của purchase order detail")
    product_variant_id: str = Field(description="ID của product variant")
    ordered_quantity: int = Field(gt=0, description="Số lượng đã đặt trong PO")
    received_quantity: int = Field(ge=0, description="Số lượng thực tế nhận được")
    accepted_quantity: int = Field(ge=0, description="Số lượng chấp nhận nhập kho")
    rejected_quantity: int = Field(ge=0, default=0, description="Số lượng từ chối")
    rejection_reason: Optional[str] = Field(None, description="Lý do từ chối nếu có")
    notes: Optional[str] = Field(None, description="Ghi chú cho item này")

class CreateGoodsReceiptRequest(BaseModel):
    purchase_order_id: str = Field(description="ID của đơn đặt hàng")
    warehouse_id: str = Field(description="ID kho nhận hàng")
    supplier_id: str = Field(description="ID nhà cung cấp")
    receipt_date: datetime = Field(default_factory=datetime.now, description="Ngày nhận hàng")
    delivery_note_number: Optional[str] = Field(None, description="Số phiếu giao hàng")
    parent_receipt_id: Optional[str] = Field(None, description="ID của GR cha (cho GR2, GR3...)")
    related_purchase_return_id: Optional[str] = Field(None, description="ID của PRO tương ứng (nếu là hàng thay thế)")
    notes: Optional[str] = Field(None, description="Ghi chú chung")
    items: List[GoodsReceiptDetailCreate] = Field(min_length=1, description="Danh sách sản phẩm nhập kho")