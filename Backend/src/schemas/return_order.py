from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class ReturnOrderSortBy(str, Enum):
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"
    TOTAL_ASC = "total_asc"
    TOTAL_DESC = "total_desc"

class ReturnOrderStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ReturnOrderActionType(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


class ReturnItemRequest(BaseModel):
    order_detail_id: str = Field(..., description="ID của chi tiết đơn hàng cần hoàn trả")
    quantity: int = Field(..., gt=0, description="Số lượng cần hoàn trả (phải > 0)")
    images: List[str] = Field(..., description="Danh sách hình ảnh sản phẩm (tối thiểu 5, tối đa 20)")

    @field_validator('images')
    @classmethod
    def validate_images_unique(cls, v):
        if len(v) != len(set(str(url) for url in v)):
            raise ValueError('Danh sách hình ảnh không được chứa URL trùng lặp')

        if not (5 <= len(v) <= 20):
            raise ValueError("Danh sách hình ảnh phải từ 5 đến 20 ảnh")

        return v

class CreateReturnRequest(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500, description="Lý do hoàn trả (10-500 ký tự)")
    note: Optional[str] = Field(None, max_length=1000, description="Ghi chú thêm (tùy chọn, tối đa 1000 ký tự)")
    return_items: List[ReturnItemRequest] = Field(..., description="Danh sách sản phẩm cần hoàn trả (1-50 items)")

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Lý do hoàn trả không được để trống hoặc chỉ chứa khoảng trắng')
        if len(v) < 10:
            raise ValueError('Lý do hoàn trả phải có ít nhất 10 ký tự')
        return v

    @field_validator('note')
    @classmethod
    def validate_note(cls, v):
        if v:
            v = v.strip()
            if not v:
                return None
        return v

    @field_validator('return_items')
    @classmethod
    def validate_unique_order_details(cls, v):
        order_detail_ids = [item.order_detail_id for item in v]
        if len(order_detail_ids) != len(set(order_detail_ids)):
            raise ValueError('Danh sách sản phẩm có order_detail_id trùng lặp')

        if not (1 <= len(v) <= 50):
            raise ValueError("Danh sách sản phẩm hoàn trả phải từ 1 đến 50")

        return v



class ProcessReturnRequest(BaseModel):
    action: ReturnOrderActionType
    admin_note: Optional[str] = Field(None, max_length=500, description="Ghi chú của admin")
    reject_reason: Optional[str] = Field(None, max_length=500, description="Lý do từ chối")
    attempt_count: Optional[int] = Field(1, ge=1, le=5, description="Số lần thử lại (1-5)")

    @field_validator('reject_reason')
    @classmethod
    def validate_reject_reason(cls, v, info):
        if info.data.get('action') == ReturnOrderActionType.REJECT and not v:
            raise ValueError('Cần cung cấp lí do khi từ chối hoàn trả')
        return v

    @field_validator('reject_reason', 'admin_note')
    @classmethod
    def validate_string_fields(cls, v):
        if v:
            v = v.strip()
            if not v:
                return None
        return v



class CompleteReturnRequest(BaseModel):
    restore_stock: bool = Field(default=True, description="Có hoàn trả sản phẩm vào kho không")
    admin_note: Optional[str] = Field(None, max_length=500, description="Ghi chú khi hoàn thành")
    force_complete: bool = Field(default=False, description="Bắt buộc hoàn thành ngay cả khi refund thất bại")

    @field_validator('admin_note')
    @classmethod
    def validate_admin_note(cls, v):
        if v:
            v = v.strip()
            if not v:
                return None
        return v



class UpdateRefundStatusRequest(BaseModel):
    status: str

