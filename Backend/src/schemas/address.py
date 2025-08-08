from typing import Optional
from pydantic import BaseModel, Field
import uuid

class AddressModel(BaseModel):
    id: uuid.UUID
    line: str
    street: str
    ward: str
    city: str
    district: str
    country: str = Field(default="Việt Nam")
    user_id: uuid.UUID

class AddressCreateModel(BaseModel):
    line: str
    street: str
    ward: str
    city: str
    district: str
    country: Optional[str] = Field(default="Việt Nam")

class AddressUpdateModel(BaseModel):
    line: Optional[str] = None
    street: Optional[str] = None
    ward: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    country: Optional[str]  = Field(default="Việt Nam")