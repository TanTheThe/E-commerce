from typing import Optional, List
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class CategoriesProductModel(BaseModel):
    id: uuid.UUID
    categories_id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime = Field(default=datetime.now)
    updated_at: datetime = None
    deleted_at: datetime = None


class CategoriesCreateModel(BaseModel):
    categories_id: str
    product_id: str