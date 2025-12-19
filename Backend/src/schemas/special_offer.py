from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid
from datetime import datetime, timezone


class OfferTypeEnum(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"

class OfferScopeEnum(str, Enum):
    ORDER = "order"
    PRODUCT = "product"

class QuantityStatusEnum(str, Enum):
    REMAINING = "remaining"
    OUT = "out"

class TimeStatusEnum(str, Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    EXPIRED = "expired"


class SpecialOfferCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Tên chương trình khuyến mãi")
    discount: int = Field(..., gt=0, le=100, description="Phần trăm giảm giá (1-100)")
    condition: Optional[int] = Field(None, ge=0, description="Điều kiện áp dụng (giá trị đơn hàng tối thiểu)")
    type: str = Field(..., pattern="^(percentage|fixed)$", description="Loại giảm giá")
    scope: str = Field(..., pattern="^(order|product)$", description="Phạm vi áp dụng")
    total_quantity: int = Field(..., gt=0, description="Tổng số lượng voucher")
    start_time: Optional[datetime] = Field(None, description="Thời gian bắt đầu")
    end_time: datetime = Field(..., description="Thời gian kết thúc")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tên không được để trống")
        return v.strip()

    @model_validator(mode='after')
    def validate_times_and_scope(self):
        if self.end_time <= self.start_time:
            raise ValueError("Thời gian kết thúc phải sau thời gian bắt đầu")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if self.start_time < now.replace(hour=0, minute=0, second=0, microsecond=0):
            raise ValueError("Thời gian bắt đầu không được trong quá khứ")

        if self.scope == "order" and self.condition is not None and self.condition <= 0:
            raise ValueError("Điều kiện đơn hàng tối thiểu phải lớn hơn 0")

        if self.scope == "product":
            self.condition = None

        return self

class SpecialOfferUpdateModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    discount: Optional[int] = Field(None, gt=0, le=100)
    condition: Optional[int] = Field(None, ge=0)
    type: Optional[str] = Field(None, pattern="^(percentage|fixed)$")
    scope: Optional[str] = Field(None, pattern="^(order|product)$")
    total_quantity: Optional[int] = Field(None, gt=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Tên không được để trống")
        return v

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def validate_datetime(cls, v):
        if v is not None and isinstance(v, datetime):
            return v.replace(tzinfo=None)
        return v

    @model_validator(mode='after')
    def validate_time_range(self):
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValueError("end_time phải sau start_time")
        return self


class SpecialOfferFilterModel(BaseModel):
    search: Optional[str] = Field(None, max_length=255, description="Tìm kiếm theo code hoặc name")
    type: Optional[OfferTypeEnum] = Field(None, description="Lọc theo loại giảm giá")
    scope: Optional[OfferScopeEnum] = Field(None, description="Lọc theo phạm vi")
    discount_min: Optional[int] = Field(None, ge=0, le=100, description="Giảm giá tối thiểu")
    discount_max: Optional[int] = Field(None, ge=0, le=100, description="Giảm giá tối đa")
    quantity_status: Optional[QuantityStatusEnum] = Field(None, description="Trạng thái số lượng")
    time_status: Optional[TimeStatusEnum] = Field(None, description="Trạng thái thời gian")

    @field_validator('search')
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if not v:
                return None
            v = v.replace('%', '\\%').replace('_', '\\_')
        return v

    @model_validator(mode='after')
    def validate_discount_range(self):
        if self.discount_min is not None and self.discount_max is not None:
            if self.discount_min > self.discount_max:
                raise ValueError("discount_min phải nhỏ hơn hoặc bằng discount_max")
        return self


class SetOfferToProduct(BaseModel):
    product_ids: List[str] = Field(..., min_length=1, max_length=100, description="Danh sách ID sản phẩm (tối đa 100)")
    special_offer_id: str = Field(..., description="ID của special offer")

    @field_validator('product_ids')
    @classmethod
    def validate_unique_products(cls, v: List[str]):
        if len(v) != len(set(v)):
            raise ValueError("Danh sách product_ids có ID trùng lặp")
        return v


class AssignOfferToUsers(BaseModel):
    special_offer_id: str = Field(..., description="ID của special offer")
    user_ids: List[str] = Field(..., min_length=1, max_length=1000, description="Danh sách user IDs (tối đa 1000)")
    admin_note: Optional[str] = Field(None, max_length=500, description="Ghi chú từ admin")
    send_notification: bool = Field(True, description="Gửi thông báo cho users")

    @field_validator('user_ids')
    @classmethod
    def validate_unique_users(cls, v: List[str]) -> List[str]:
        if len(v) != len(set(v)):
            raise ValueError("Danh sách user_ids có ID trùng lặp")
        return v

    @field_validator('admin_note')
    @classmethod
    def validate_admin_note(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v