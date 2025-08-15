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
    transaction_no: str
    order_detail: List[OrderDetailModel]
    user_id: uuid.UUID
    special_offer_id: uuid.UUID

class OrderCreateModel(BaseModel):
    special_offer_id: Optional[str]
    note: Optional[str]
    order_detail: List[OrderDetailCreateModel]
    address_id: str

class StatusUpdateModel(BaseModel):
    status: str

class CheckOut(BaseModel):
    payment_method: str = Field(default="vnpay")
    transaction_no: Optional[str]

class OrderFilterModel(BaseModel):
    search: Optional[str] = None
    sort_by_total_price: Optional[str] = None
    sort_by_created_at: Optional[str] = None
    status: Optional[str] = None