from pydantic import BaseModel
from typing import Optional, List
import uuid


class CartCreateModel(BaseModel):
    product_variant_id: uuid.UUID
    quantity: int

class CartItemCreateModel(BaseModel):
    cart_id: uuid.UUID
    product_id: uuid.UUID
    product_variant_id: uuid.UUID
    quantity: int
    price: int

class CartItemsDeleteModel(BaseModel):
    item_ids: List[str]

