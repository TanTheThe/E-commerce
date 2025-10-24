from typing import Optional, List
from pydantic import BaseModel

class BrandCreateModel(BaseModel):
    name: str
    logo: Optional[str] = None
    is_active: bool = True
    
class BrandUpdateModel(BaseModel):
    name: Optional[str] = None
    logo: Optional[str] = None
    is_active: Optional[bool] = None
    
class DeleteMultipleBrandsModel(BaseModel):
    brand_ids: List[str]