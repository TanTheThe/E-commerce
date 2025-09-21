from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class MaterialCreateModel(BaseModel):
    name: str
    is_active: bool = True

class MaterialUpdateModel(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    
class DeleteMultipleMaterialsModel(BaseModel):
    material_ids: List[str]

class ProductMaterialAssignmentModel(BaseModel):
    product_id: str
    materials: List[Dict[str, Any]]