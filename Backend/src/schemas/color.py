from pydantic import BaseModel
from typing import Optional
import uuid


class Color(BaseModel):
    id: uuid.UUID
    name: str

class ColorCreateModel(BaseModel):
    name: str
    code: str

class ColorUpdateModel(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None

class ColorFilterModel(BaseModel):
    search: Optional[str] = None
