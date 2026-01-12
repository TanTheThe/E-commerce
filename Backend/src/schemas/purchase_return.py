from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

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
    
class PurchaseReturnStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    SENT = "sent"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
class SortBy(str, Enum):
    RETURN_DATE_ASC = "return_date_asc"
    RETURN_DATE_DESC = "return_date_desc"
    TOTAL_AMOUNT_ASC = "total_return_amount_asc"
    TOTAL_AMOUNT_DESC = "total_return_amount_desc"
    CREATED_AT_ASC = "created_at_asc"
    CREATED_AT_DESC = "created_at_desc"    



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




class SendEmailRequest(BaseModel):
    supplier_email: Optional[str] = None
    
    @field_validator('supplier_email')
    @classmethod
    def validate_supplier_email(cls, v):
        if v:
            if len(v) > 255:
                raise ValueError("Email quá dài")
        return v



class GetPurchaseReturnsQuery(BaseModel):
    warehouse_id: str
    status_pr: Optional[PurchaseReturnStatus] = None
    return_type: Optional[ReturnType] = None
    purchase_order_id: Optional[str] = None
    goods_receipt_id: Optional[str] = None
    supplier_id: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    search: Optional[str] = Field(None, max_length=100)
    sort_by: Optional[SortBy] = SortBy.RETURN_DATE_DESC
    
    @field_validator('search')
    @classmethod
    def validate_search(cls, v):
        if v:
            v = v.strip()
            if any(char in v for char in [';', '--', '/*', '*/', 'xp_', 'sp_']):
                raise ValueError("Từ khóa tìm kiếm không hợp lệ")
        return v
    
    @model_validator(mode='after')
    def validate_date_range(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValueError("from_date phải nhỏ hơn hoặc bằng to_date")
            
            delta = self.to_date - self.from_date
            if delta.days > 365:
                raise ValueError("Khoảng thời gian tìm kiếm không được vượt quá 1 năm")
        
        return self





class ReturnDetailUpdate(BaseModel):
    id: Optional[str] = Field(None, description="ID của detail (nếu có = update, không có = create mới)")
    product_variant_id: str
    goods_receipt_detail_id: Optional[str] = Field(None, description="ID của goods receipt detail")
    return_quantity: int = Field(..., gt=0, le=10000, description="Số lượng trả lại")
    unit_cost: int = Field(..., gt=0, description="Giá nhập ban đầu")
    condition: Optional[ReturnCondition] = Field(ReturnCondition.DAMAGED, description="Tình trạng hàng")
    rejection_evidence: Optional[List[str]] = Field(None, max_length=10, description="Hình ảnh/chứng từ")
    notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator('rejection_evidence')
    @classmethod
    def validate_evidence(cls, v):
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
    

class UpdatePurchaseReturnRequest(BaseModel):
    return_date: Optional[datetime] = Field(None, description="Ngày tạo phiếu trả hàng")
    return_type: Optional[ReturnType] = Field(None, description="Loại trả hàng")
    return_reason: Optional[str] = Field(None, min_length=10, max_length=500, description="Lý do trả hàng")
    delivery_note_number: Optional[str] = Field(None, max_length=100, description="Số phiếu giao nhận")
    refund_amount: Optional[int] = Field(None, ge=0, description="Số tiền hoàn lại")
    notes: Optional[str] = Field(None, max_length=1000, description="Ghi chú chung")
    return_details: Optional[List[ReturnDetailUpdate]] = Field(None, min_length=1, max_length=100, description="Danh sách chi tiết")
    
    @field_validator('return_reason')
    @classmethod
    def validate_return_reason(cls, v):
        if v:
            v = v.strip()
            if len(v) < 10:
                raise ValueError("Lý do hoàn trả phải có ít nhất 10 ký tự")
        return v

    @field_validator('delivery_note_number', 'notes')
    @classmethod
    def validate_strings(cls, v):
        return v.strip() if v else None

    @model_validator(mode='after')
    def validate_return_date(self):
        if self.return_date:
            if self.return_date > datetime.now():
                raise ValueError("Ngày hoàn trả không được ở tương lai")
        return self
    
    @model_validator(mode='after')
    def validate_unique_details(self):
        if self.return_details:
            seen = set()
            for detail in self.return_details:
                key = (detail.product_variant_id, detail.goods_receipt_detail_id)
                if key in seen:
                    raise ValueError(
                        f"Trùng lặp sản phẩm variant {detail.product_variant_id} "
                        f"trong cùng goods receipt detail"
                    )
                seen.add(key)
        return self
