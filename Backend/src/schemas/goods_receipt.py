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
    notes: Optional[str] = Field(None, description="Ghi chú chung")
    items: List[GoodsReceiptDetailCreate] = Field(min_length=1, description="Danh sách sản phẩm nhập kho")
    
class ReceiptDetailUpdate(BaseModel):
    id: Optional[str] = Field(None, description="ID của detail (nếu có = update, không có = create mới)")
    product_variant_id: str
    po_detail_id: str = Field(..., description="ID của purchase order detail (bắt buộc)")
    ordered_quantity: int = Field(..., ge=0, description="Số lượng đặt hàng ban đầu trong PO")
    received_quantity: int = Field(..., ge=0, description="Số lượng thực nhận từ nhà cung cấp")
    accepted_quantity: int = Field(..., ge=0, description="Số lượng chấp nhận nhập kho")
    rejected_quantity: int = Field(default=0, ge=0, description="Số lượng từ chối")
    unit_cost: int = Field(..., gt=0, description="Giá nhập trên mỗi đơn vị")
    rejection_reason: Optional[str] = Field(None, description="Lý do từ chối nếu có rejected_quantity")
    notes: Optional[str] = None


class UpdateGoodsReceiptRequest(BaseModel):
    receipt_date: Optional[datetime] = Field(None, description="Ngày nhận hàng thực tế")
    delivery_note_number: Optional[str] = Field(None, description="Số phiếu giao hàng của NCC")
    has_discrepancy: Optional[bool] = Field(None, description="Có sai lệch không?")
    discrepancy_notes: Optional[str] = Field(None, description="Ghi chú về sai lệch")
    notes: Optional[str] = Field(None, description="Ghi chú chung")
    receipt_details: Optional[List[ReceiptDetailUpdate]] = Field(None, description="Danh sách chi tiết nhập kho")


class SortBy(str, Enum):
    receipt_date_asc = "receipt_date_asc"
    receipt_date_desc = "receipt_date_desc"
    created_at_asc = "created_at_asc"
    created_at_desc = "created_at_desc"
    total_amount_asc = "total_amount_asc"
    total_amount_desc = "total_amount_desc"