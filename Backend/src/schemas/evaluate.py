from typing import Optional
from pydantic import BaseModel
import uuid


class EvaluateModel(BaseModel):
    id: uuid.UUID
    comment: Optional[str] = None
    rate: int
    image: Optional[str] = None
    product_id: uuid.UUID
    order_detail_id: uuid.UUID


class EvaluateInputModel(BaseModel):
    comment: Optional[str] = None
    rate: int
    image: Optional[str] = None
    order_detail_id: str


class EvaluateCreateModel(BaseModel):
    comment: Optional[str] = None
    rate: int
    image: Optional[str] = None
    order_detail_id: str
    product_id: str
    product_variant_id: str
    user_id: str


class EvaluateReadModel(BaseModel):
    comment: Optional[str] = None
    rate: int
    image: Optional[str] = None

class SupplementEvaluateModel(BaseModel):
    additional_comment: str = None
    additional_image: Optional[str] = None

class GetEvaluateByProduct(BaseModel):
    product_variant_id: Optional[str] = None
    rate: Optional[int] = None

class EvaluateFilterModel(BaseModel):
    search: Optional[str] = None
    rate: Optional[int] = None
    sort_by_created_at: Optional[str] = None
    sort_by_rate: Optional[str] = None