from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class NotificationCreateModel(BaseModel):
    id: uuid.UUID
    recipient_type: str
    recipient_id: Optional[uuid.UUID]
    sender_type: str
    sender_id: Optional[uuid.UUID]
    type: str
    title: str
    message: str
    order_id: Optional[uuid.UUID]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime


class MarkAsReadRequest(BaseModel):
    notification_ids: List[str]

class MarkAsProcessedRequest(BaseModel):
    notification_id: str


class NotificationType:
    ORDER_CANCELLED = "order_cancelled"
    ORDER_CANCELLATION_REQUEST = "order_cancellation_request"
    ORDER_CANCELLATION_APPROVED = "order_cancellation_approved"
    ORDER_CANCELLATION_REJECTED = "order_cancellation_rejected"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_DELIVERED = "order_delivered"
    ORDER_SHIPPING = "order_shipping"


class ActionType:
    HANDLE_CANCELLATION = "handle_cancellation"


class RecipientType:
    ADMIN = "admin"
    CUSTOMER = "customer"
