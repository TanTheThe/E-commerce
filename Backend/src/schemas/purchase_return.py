from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


class ReturnItemRequest(BaseModel):
    gr_detail_id: str
    return_quantity: int
    condition: str = Field(default="damaged")
    rejection_evidence: Optional[List[str]] = None
    notes: Optional[str] = None


class CreatePurchaseReturnRequest(BaseModel):
    goods_receipt_id: str
    return_items: List[ReturnItemRequest]
    return_reason: str
    return_type: str = Field(default="exchange")
    notes: Optional[str] = None
    
class SortBy(str, Enum):
    return_date_asc = "return_date_asc"
    return_date_desc = "return_date_desc"
    total_return_amount_asc = "total_return_amount_asc"
    total_return_amount_desc = "total_return_amount_desc"

class ReturnDetailUpdate(BaseModel):
    id: Optional[str] = Field(None, description="ID của detail (nếu có = update, không có = create mới)")
    product_variant_id: str
    goods_receipt_detail_id: Optional[str] = Field(None, description="ID của goods receipt detail (nếu trả từ phiếu nhập cụ thể)")
    return_quantity: int = Field(..., gt=0, description="Số lượng trả lại cho nhà cung cấp")
    unit_cost: int = Field(..., gt=0, description="Giá nhập ban đầu của sản phẩm")
    condition: Optional[str] = Field(None, description="Tình trạng hàng trả: damaged, defective, expired, wrong_item")
    rejection_evidence: Optional[List[str]] = Field(None, description="Hình ảnh/chứng từ về hàng reject")
    notes: Optional[str] = None

class UpdatePurchaseReturnRequest(BaseModel):
    return_date: Optional[datetime] = Field(None, description="Ngày tạo phiếu trả hàng")
    return_type: Optional[str] = Field(None, description="Loại trả hàng: return_to_supplier, exchange, refund")
    return_reason: Optional[str] = Field(None, description="Lý do trả hàng chung")
    delivery_note_number: Optional[str] = Field(None, description="Số phiếu giao nhận trả hàng (do NCC cung cấp)")
    refund_amount: Optional[int] = Field(None, ge=0, description="Số tiền NCC đồng ý hoàn lại")
    notes: Optional[str] = Field(None, description="Ghi chú chung")
    return_details: Optional[List[ReturnDetailUpdate]] = Field(None, description="Danh sách chi tiết phiếu trả hàng")
