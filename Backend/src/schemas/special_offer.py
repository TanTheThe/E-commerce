from typing import Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class SpecialOfferModel(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    discount: int
    condition: Optional[int]
    type: str
    total_quantity: int
    used_quantity: int = Field(default=0)
    start_time: datetime = Field(default=datetime.now())
    end_time: datetime


class SpecialOfferCreateModel(BaseModel):
    name: str
    discount: int
    condition: Optional[int]
    type: str
    total_quantity: int
    start_time: Optional[datetime] = Field(default=datetime.now())
    end_time: datetime


class SpecialOfferUpdateModel(BaseModel):
    name: Optional[str] = None
    discount: Optional[int] = None
    condition: Optional[int] = None
    type: Optional[str] = None
    total_quantity: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None