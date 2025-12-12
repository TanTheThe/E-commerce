from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

class OrderDetailModel(BaseModel):
    id: uuid.UUID
    quantity: int
    price: int
    product: Optional[dict]
    product_id: uuid.UUID
    product_variant_id: uuid.UUID
    order_id: uuid.UUID

class OrderDetailCreateModel(BaseModel):
    quantity: int = Field(gt=0, le=100, description="Số lượng phải > 0 và <= 100")
    product_variant_id: str = Field(min_length=1, max_length=36)