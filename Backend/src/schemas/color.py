from pydantic import BaseModel
import uuid


class Color(BaseModel):
    id: uuid.UUID
    name: str

class ColorCreateModel(BaseModel):
    name: str