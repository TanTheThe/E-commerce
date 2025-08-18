from pydantic import BaseModel
import uuid
from typing import Optional

class CategoriesModel(BaseModel):
    id: uuid.UUID
    name: str
    images: str


class CategoriesCreateModel(BaseModel):
    name: str
    image: str
    parent_id: Optional[uuid.UUID] = None
    type_size: str

class CategoriesUpdateModel(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    type_size: Optional[str] = None

class CategoriesFilterModel(BaseModel):
    search: Optional[str] = None
    parent_id: Optional[str] = None
    type_size: Optional[str] = None