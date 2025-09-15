from pydantic import BaseModel

class PaymentRequest(BaseModel):
    order_type: str
    order_code: str
    amount: int
    order_desc: str
    bank_code: str = ""
    language: str = ""

class PaymentStatusType:
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"