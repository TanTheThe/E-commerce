from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


class ReturnItemRequest(BaseModel):
    gr_detail_id: str
    return_quantity: int
    condition: str = Field(default="damaged")
    rejection_evidence: Optional[List[str]] = None
    notes: Optional[str] = None


class CreatePurchaseReturnRequest(BaseModel):
    goods_receipt_id: str
    return_items: List[ReturnItemRequest]
    return_reason: str
    return_type: str = Field(default="exchange")
    notes: Optional[str] = None


class CompletePurchaseReturnRequest(BaseModel):
    shipped_date: Optional[datetime] = None
    refund_amount: Optional[int] = None
    notes: Optional[str] = None
    
class SortBy(str, Enum):
    return_date_asc = "return_date_asc"
    return_date_desc = "return_date_desc"
    total_return_amount_asc = "total_return_amount_asc"
    total_return_amount_desc = "total_return_amount_desc"
