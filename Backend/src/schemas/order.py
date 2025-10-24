from typing import Optional, List
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from src.schemas.order_detail import OrderDetailModel, OrderDetailCreateModel


class OrderModel(BaseModel):
    id: uuid.UUID
    code: str
    sub_total: int
    total_price: int
    discount: Optional[int] = Field(default=0)
    note: Optional[str]
    created_at: datetime = Field(default=datetime.now)
    status: str
    payment_method: str = Field(default="vnpay")
    payment_status: str
    order_detail: List[OrderDetailModel]
    user_id: uuid.UUID
    special_offer_id: uuid.UUID

class OrderCreateModel(BaseModel):
    special_offer_id: Optional[str] = None
    note: Optional[str] = None
    payment_method: str = "direct"
    order_detail: List[OrderDetailCreateModel]
    address_id: str

class StatusUpdateModel(BaseModel):
    status: str

class CheckOut(BaseModel):
    payment_method: str = Field(default="vnpay")
    payment_status: str = Field(default="pending")

class OrderFilterModel(BaseModel):
    search: Optional[str] = None
    sort_by_total_price: Optional[str] = None
    sort_by_created_at: Optional[str] = None
    status: Optional[str] = None

class CancelOrderRequest(BaseModel):
    reason: str
    reason_detail: Optional[str] = None

class ProcessCancellationRequest(BaseModel):
    action: str # handle_cancellation
    admin_note: Optional[str] = None
    reject_reason: Optional[str] = None

class CancellationStatusType:
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"

class PaymentStatusOrderType:
    PENDING = "pending"
    REFUNDED = "refunded"
    SUCCESS = "success"
    FAILED = "failed"
