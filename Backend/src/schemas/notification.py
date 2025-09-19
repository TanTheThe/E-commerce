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
    ORDER_RECEIVED = "order_received"
    ORDER_SHIPPING = "order_shipping"
    SPECIAL_OFFER_ASSIGNED = "special_offer_assigned"
    RETURN_ORDER_REQUEST = "return_order_request"
    RETURN_ORDER_APPROVED = "return_order_approved"
    RETURN_ORDER_REJECTED = "return_order_rejected"
    RETURN_ORDER_COMPLETED = "return_order_completed"


class ActionType:
    HANDLE_CANCELLATION = "handle_cancellation"
    HANDLE_RETURN = "handle_return"


class RecipientType:
    ADMIN = "admin"
    CUSTOMER = "customer"
