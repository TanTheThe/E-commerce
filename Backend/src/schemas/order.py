from enum import Enum
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, model_validator, field_validator
import uuid
from datetime import datetime, timedelta
from src.schemas.order_detail import OrderDetailModel, OrderDetailCreateModel


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPING = "shipping"
    DELIVERED = "delivered"
    RECEIVED = "received"
    CANCELLED = "cancelled"
    RETURNED = "returned"


STATUS_TRANSITION_RULES = {
    OrderStatus.PENDING: {
        "allowed_next": [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        "description": "Đơn hàng chờ xác nhận"
    },
    OrderStatus.CONFIRMED: {
        "allowed_next": [OrderStatus.SHIPPING, OrderStatus.PENDING, OrderStatus.CANCELLED],
        "description": "Đơn hàng đã xác nhận"
    },
    OrderStatus.SHIPPING: {
        "allowed_next": [OrderStatus.DELIVERED, OrderStatus.CONFIRMED],
        "description": "Đơn hàng đang giao"
    },
    OrderStatus.DELIVERED: {
        "allowed_next": [OrderStatus.RECEIVED],
        "description": "Đơn hàng đã giao"
    },
    OrderStatus.RECEIVED: {
        "allowed_next": [],
        "description": "Đơn hàng đã hoàn thành"
    },
    OrderStatus.CANCELLED: {
        "allowed_next": [],
        "description": "Đơn hàng đã hủy"
    }
}


class CancellationStatusType(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"

class PaymentStatusOrderType(str, Enum):
    PENDING = "pending"
    REFUNDED = "refunded"
    SUCCESS = "success"
    FAILED = "failed"

class CancellationAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"

class StatisticsPeriod(str, Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    CUSTOM = "custom"

class OrderStatisticsType(str, Enum):
    COUNT = "count"
    SALES = "sales"
    REVENUE = "revenue"
    AVERAGE_ORDER_VALUE = "average_order_value"


CANCELLATION_REASONS = {
    "change_mind": "Tôi đã thay đổi ý định",
    "wrong_product": "Đặt nhầm sản phẩm",
    "wrong_address": "Sai địa chỉ giao hàng",
    "payment_issue": "Vấn đề về thanh toán",
    "delivery_time": "Thời gian giao hàng không phù hợp",
    "found_better_price": "Tìm được giá tốt hơn ở nơi khác",
    "other": "Lý do khác"
}


class OrderCreateModel(BaseModel):
    special_offer_id: Optional[str] = Field(None, max_length=36)
    note: Optional[str] = Field(None, max_length=500)
    payment_method: str = "direct"
    order_detail: List[OrderDetailCreateModel] = Field(min_length=1, max_length=50)
    address_id: str = Field(min_length=1, max_length=36)

    @model_validator(mode='after')
    def validate_order(self):
        variant_ids = [item.product_variant_id for item in self.order_detail]
        if len(variant_ids) != len(set(variant_ids)):
            raise ValueError("Không được đặt trùng sản phẩm. Vui lòng tăng số lượng thay vì thêm nhiều dòng.")

        total_quantity = sum(item.quantity for item in self.order_detail)
        if total_quantity > 500:
            raise ValueError("Tổng số lượng sản phẩm không được vượt quá 500")

        return self


class StatusUpdateModel(BaseModel):
    status: str
    note: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional notes for status update"
    )

    @field_validator('note')
    @classmethod
    def validate_note(cls, v):
        if v:
            v = v.strip()
            if len(v) == 0:
                return None
        return v


class OrderFilterModel(BaseModel):
    search: Optional[str] = Field(None, max_length=100)
    status: Optional[OrderStatus] = None
    sort_by_total_price: Optional[Literal["cheapest", "most_expensive"]] = None
    sort_by_created_at: Optional[Literal["newest", "oldest"]] = None

    @field_validator('search')
    @classmethod
    def validate_search(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None

            dangerous_patterns = ['--', ';', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute']
            v_lower = v.lower()
            if any(pattern in v_lower for pattern in dangerous_patterns):
                raise ValueError("Tìm kiếm chứa ký tự không hợp lệ")
        return v

    @field_validator('sort_by_total_price', 'sort_by_created_at')
    @classmethod
    def validate_sort(cls, v):
        if v:
            v = v.lower().strip()
        return v


class CancelOrderRequest(BaseModel):
    reason: str = Field(..., description="Cancellation reason key")
    reason_detail: Optional[str] = Field(None, max_length=500)

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if v not in CANCELLATION_REASONS:
            raise ValueError(f"Invalid reason. Must be one of: {', '.join(CANCELLATION_REASONS.keys())}")
        return v

    @field_validator('reason_detail')
    @classmethod
    def validate_reason_detail(cls, v, values):
        if values.get('reason') == 'other' and not v:
            raise ValueError("reason_detail is required when reason is 'other'")
        return v.strip() if v else None


class ProcessCancellationRequest(BaseModel):
    action: CancellationStatusType = Field(..., description="Action to perform: approve or reject")
    admin_note: Optional[str] = Field(None, max_length=500, description="Admin note for approval")
    reject_reason: Optional[str] = Field(None, max_length=500, description="Reason for rejection")

    @field_validator('reject_reason')
    @classmethod
    def validate_reject_reason(cls, v, values):
        if values.get('action') == CancellationStatusType.REJECTED and not v:
            raise ValueError("reject_reason is required when action is 'reject'")
        return v

    @field_validator('reject_reason')
    @classmethod
    def validate_reject_reason_content(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError("reject_reason must be at least 10 characters")
        return v.strip() if v else None


class DateRangeCalculator:

    @staticmethod
    def get_date_range(from_date: Optional[datetime], to_date: Optional[datetime], period: StatisticsPeriod):
        if from_date and to_date:
            return from_date, to_date

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        if period == StatisticsPeriod.TODAY:
            return today_start, today_end

        elif period == StatisticsPeriod.YESTERDAY:
            yesterday_start = today_start - timedelta(days=1)
            yesterday_end = yesterday_start.replace(hour=23, minute=59, second=59)
            return yesterday_start, yesterday_end

        elif period == StatisticsPeriod.LAST_7_DAYS:
            from_date = today_start - timedelta(days=6)
            return from_date, today_end

        elif period == StatisticsPeriod.LAST_30_DAYS:
            from_date = today_start - timedelta(days=29)
            return from_date, today_end

        elif period == StatisticsPeriod.THIS_MONTH:
            from_date = today_start.replace(day=1)
            return from_date, today_end

        elif period == StatisticsPeriod.LAST_MONTH:
            first_day_this_month = today_start.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)
            return (
                first_day_last_month,
                last_day_last_month.replace(hour=23, minute=59, second=59)
            )

        return today_start - timedelta(days=6), today_end

