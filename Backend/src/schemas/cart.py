from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import uuid

MAX_QUANTITY_PER_ITEM = 999

class CartCreateModel(BaseModel):
    product_variant_id: str
    quantity: int = Field(gt=0, le=MAX_QUANTITY_PER_ITEM)

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: str):
        if v <= 0:
            raise ValueError('Số lượng sản phẩm phải lớn hơn bằng 0')
        if v > MAX_QUANTITY_PER_ITEM:
            raise ValueError(f'Số lượng sản phẩm không được vượt quá {MAX_QUANTITY_PER_ITEM}')
        return v
    
class CartItemCreateModel(BaseModel):
    cart_id: uuid.UUID
    product_id: uuid.UUID
    product_variant_id: uuid.UUID
    quantity: int
    price: int

class CartItemsDeleteModel(BaseModel):
    item_ids: List[str] = Field(
        min_items=1,
        max_items=100,
        description="List of cart item IDs to delete"
    )
    @field_validator('item_ids')
    @classmethod
    def validate_item_ids(cls, v: str):
        if not v:
            raise ValueError('item_ids cannot be empty')
        
        if len(v) > 100:
            raise ValueError(f'Cannot delete more than 100 items at once')
        
        if len(v) != len(set(v)):
            raise ValueError('item_ids contains duplicates')
        
        return v

