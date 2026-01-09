from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid


class ReturnCondition(str, Enum):
    DAMAGED = "damaged"
    DEFECTIVE = "defective"
    EXPIRED = "expired"
    WRONG_ITEM = "wrong_item"
    OTHER = "other"

class ReturnType(str, Enum):
    EXCHANGE = "exchange"
    REFUND = "refund"
    CREDIT_NOTE = "credit_note"

class ReturnItemRequest(BaseModel):
    gr_detail_id: str
    return_quantity: int
    condition: ReturnCondition = Field(default=ReturnCondition.DAMAGED)
    rejection_evidence: Optional[List[str]] = Field(default=None, max_length=10)
    notes: Optional[str] = Field(default=None, max_length=500)

    @field_validator('return_quantity')
    @classmethod
    def validate_return_quantity(cls, v):
        if v <= 0:
            raise ValueError("Số lượng hoàn trả phải lớn hơn 0")
        if v > 10000:
            raise ValueError("Số lượng hoàn trả không hợp lệ")
        return v

    @field_validator('rejection_evidence')
    @classmethod
    def validate_rejection_evidence(cls, v):
        if v:
            if len(v) > 10:
                raise ValueError("Tối đa 10 file bằng chứng")
            for url in v:
                if not url or not url.strip():
                    raise ValueError("URL bằng chứng không hợp lệ")
        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v and len(v.strip()) > 500:
            raise ValueError("Ghi chú không được vượt quá 500 ký tự")
        return v.strip() if v else None

class CreatePurchaseReturnRequest(BaseModel):
    goods_receipt_id: str
    return_items: List[ReturnItemRequest] = Field(min_length=1, max_length=100)
    return_reason: str = Field(min_length=1, max_length=500)
    return_type: ReturnType = Field(default=ReturnType.EXCHANGE)
    notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator('return_reason')
    @classmethod
    def validate_return_reason(cls, v):
        if not v or not v.strip():
            raise ValueError("Lý do hoàn trả không được để trống")
        if len(v.strip()) < 10:
            raise ValueError("Lý do hoàn trả phải có ít nhất 10 ký tự")
        return v.strip()

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v and len(v.strip()) > 1000:
            raise ValueError("Ghi chú không được vượt quá 1000 ký tự")
        return v.strip() if v else None

    @model_validator(mode='after')
    def validate_unique_items(self):
        gr_detail_ids = [item.gr_detail_id for item in self.return_items]
        if len(gr_detail_ids) != len(set(gr_detail_ids)):
            raise ValueError("Không được trùng lặp sản phẩm trong đơn hoàn trả")
        return self




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
