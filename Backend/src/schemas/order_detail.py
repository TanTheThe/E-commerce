from typing import Optional, List
from pydantic import BaseModel
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
    quantity: int
    product_variant_id: str