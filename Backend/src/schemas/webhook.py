from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re
from src.schemas.order import OrderStatus


class ShippingWebhookRequest(BaseModel):
    order_code: str = Field(..., min_length=5, max_length=50, description="Mã đơn hàng")
    status: OrderStatus = Field(..., description="Trạng thái mới của đơn hàng")
    note: Optional[str] = Field(None, max_length=500, description="Ghi chú")
    timestamp: datetime = Field(default_factory=datetime.now, description="Thời gian cập nhật")
    webhook_id: Optional[str] = Field(None, description="ID duy nhất của webhook để đảm bảo idempotency")

    @field_validator('order_code')
    @classmethod
    def validate_order_code(cls, v):
        match = re.match(r'^ORD(\d{8})([A-F0-9]{8})$', v)
        if not match:
            raise ValueError('Mã đơn hàng không đúng định dạng (ORDYYYYMMDDxxxxxxxx)')
        return v

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v):
        if (datetime.now() - v).total_seconds() > 300:
            raise ValueError('Webhook đã hết hạn (quá 5 phút)')
        return v


