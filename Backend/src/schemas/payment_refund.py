from pydantic import BaseModel

class PaymentRefundModel(BaseModel):
    payment_id: str
    refund_type: str
    refund_amount: int
    refund_reason: str
    status: str

class PaymentRefundStatusType:
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"