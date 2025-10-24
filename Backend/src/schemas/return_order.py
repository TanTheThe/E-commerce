from typing import Optional, List
from pydantic import BaseModel, Field


class ReturnOrderType:
    PENDING = "pending"
    REFUNDED = "refunded"
    SUCCESS = "success"
    FAILED = "failed"

class ReturnOrderActionType:
    PENDING = "pending"
    APPROVE = "approve"
    REJECT = "reject"

class ReturnOrderStatusType:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

class ReturnItemRequest(BaseModel):
    order_detail_id: str
    quantity: int
    images: List[str]

class CreateReturnRequest(BaseModel):
    reason: str
    note: Optional[str] = None
    return_items: List[ReturnItemRequest]

class ProcessReturnRequest(BaseModel):
    action: str
    admin_note: Optional[str]
    reject_reason: Optional[str]
    attempt_count: Optional[int] = 1

class CompleteReturnRequest(BaseModel):
    restore_stock: bool = Field(default=True)

class UpdateRefundStatusRequest(BaseModel):
    status: str

