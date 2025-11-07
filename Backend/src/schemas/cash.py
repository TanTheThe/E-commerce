from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List
import uuid


class CreateManualRefundRequest(BaseModel):
    return_order_id: str = Field(..., description="ID của return order")
    amount: int = Field(..., gt=0, description="Số tiền hoàn lại (VND)")
    payment_method: str = Field(
        ...,
        description="Phương thức thanh toán: cash, bank_transfer, e_wallet"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Ghi chú thêm (VD: Số tài khoản đã chuyển, ngân hàng...)"
    )
    transaction_date: Optional[datetime] = Field(
        None,
        description="Ngày giao dịch (mặc định là hiện tại)"
    )


