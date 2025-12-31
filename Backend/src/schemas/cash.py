from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class PaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    E_WALLET = "e_wallet"
    MOMO = "momo"
    ZALOPAY = "zalopay"
    VNPAY = "vnpay"

class RefundStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"

class CreateManualRefundRequest(BaseModel):
    return_order_id: str = Field(..., description="ID của return order")
    amount: int = Field(..., gt=0, le=1_000_000_000, description="Số tiền hoàn lại (VND), tối đa 1 tỷ")
    payment_method: PaymentMethod = Field(..., description="Phương thức thanh toán")
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Ghi chú thêm (VD: Số tài khoản đã chuyển, ngân hàng...)"
    )
    transaction_date: Optional[datetime] = Field(
        None,
        description="Ngày giao dịch (mặc định là hiện tại, không được là tương lai)"
    )
    idempotency_key: Optional[str] = Field(
        None,
        min_length=10,
        max_length=100,
        description="Key để đảm bảo không tạo duplicate transaction"
    )

    @field_validator('transaction_date')
    @classmethod
    def validate_transaction_date(cls, v):
        if v and v > datetime.now():
            raise ValueError('Ngày giao dịch không được là tương lai')

        if v and (datetime.now() - v).days > 90:
            raise ValueError('Ngày giao dịch không được quá 90 ngày trước')

        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v, values):
        payment_method = values.get('payment_method')
        if payment_method in [PaymentMethod.BANK_TRANSFER, PaymentMethod.E_WALLET]:
            if not v or len(v.strip()) < 10:
                raise ValueError(f'Phương thức {payment_method} yêu cầu ghi chú chi tiết (tối thiểu 10 ký tự)')
        return v



