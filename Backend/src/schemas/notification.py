from fastapi import HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime
import uuid


class MarkAsReadRequest(BaseModel):
    notification_ids: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Danh sách ID thông báo cần đánh dấu đã đọc (tối đa 100)"
    )

    @field_validator('notification_ids')
    @classmethod
    def validate_notification_ids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Danh sách notification_ids không được rỗng")
        v = list(set(v))
        return v

class MarkAsProcessedRequest(BaseModel):
    notification_id: str


class NotificationFilterParams(BaseModel):
    unread_only: bool = Field(False, description="Chỉ lấy thông báo chưa đọc")

    notification_type: Optional[str] = Field(None, description="Lọc theo loại thông báo")
    from_date: Optional[datetime] = Field(None, description="Lọc từ ngày")
    to_date: Optional[datetime] = Field(None, description="Lọc đến ngày")

    sort_by: Literal["created_at", "read_at"] = Field("created_at", description="Sắp xếp theo trường")
    sort_order: Literal["asc", "desc"] = Field("desc", description="Thứ tự sắp xếp")



class NotificationType:
    ORDER_CANCELLED = "order_cancelled"
    ORDER_CANCELLATION_REQUEST = "order_cancellation_request"
    ORDER_CANCELLATION_APPROVED = "order_cancellation_approved"
    ORDER_CANCELLATION_REJECTED = "order_cancellation_rejected"
    ORDER_STATUS = "order_status"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_DELIVERED = "order_delivered"
    ORDER_RECEIVED = "order_received"
    ORDER_SHIPPING = "order_shipping"
    ORDER_COMPLETED = "order_completed"
    ORDER_COMPLETED_ADMIN = "order_completed_admin"
    SPECIAL_OFFER = "special_offer"
    SPECIAL_OFFER_ASSIGNED = "special_offer_assigned"
    RETURN_ORDER_REQUEST = "return_order_request"
    RETURN_ORDER_APPROVED = "return_order_approved"
    RETURN_ORDER_REJECTED = "return_order_rejected"
    RETURN_ORDER_COMPLETED = "return_order_completed"


class ActionType:
    HANDLE_CANCELLATION = "handle_cancellation"
    HANDLE_RETURN = "handle_return"
    VIEW_ORDER = "view_order"
    TRACK_ORDER = "track_order"
    CONFIRM_RECEIVED = "confirm_received"
    REVIEW_ORDER = "review_order"

class RecipientType:
    ADMIN = "admin"
    CUSTOMER = "customer"
    SYSTEM = "system"

class SenderType:
    ADMIN = "admin"
    CUSTOMER = "customer"

class NotificationValidator:
    MAX_TITLE_LENGTH = 200
    MAX_MESSAGE_LENGTH = 1000
    MAX_REASON_LENGTH = 500
    MAX_NOTE_LENGTH = 500

    @staticmethod
    def validate_string_length(value: Optional[str], field_name: str, max_length: int) -> Optional[str]:
        if value and len(value) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} không được vượt quá {max_length} ký tự"
            )
        return value

    @staticmethod
    def validate_required_string(value: Optional[str], field_name: str) -> str:
        if not value or not value.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} là bắt buộc"
            )
        return value.strip()


