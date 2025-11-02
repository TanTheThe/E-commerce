from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ShippingWebhookRequest(BaseModel):
    order_code: str = Field(..., description="Mã đơn hàng")
    status: str = Field(..., description="Trạng thái mới của đơn hàng")
    note: Optional[str] = Field(None, description="Ghi chú")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Thời gian cập nhật")


