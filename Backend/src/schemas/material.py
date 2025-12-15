from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid


class MaterialCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Tên chất liệu không được để trống')
        if len(v.strip()) < 2:
            raise ValueError('Tên chất liệu phải có ít nhất 2 ký tự')
        return v.strip()


class MaterialUpdateModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên chất liệu")
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Tên chất liệu không được để trống hoặc chỉ chứa khoảng trắng')

            if len(v) < 2:
                raise ValueError('Tên chất liệu phải có ít nhất 2 ký tự')
        return v

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        if self.name is None and self.is_active is None:
            raise ValueError('Phải cập nhật ít nhất một trường (name hoặc is_active)')
        return self

    
class DeleteMultipleMaterialsModel(BaseModel):
    material_ids: List[str]


class MaterialAssignmentItem(BaseModel):
    material_id: str = Field(..., description="ID của chất liệu")
    percentage: float = Field(..., ge=0, le=100, description="Phần trăm chất liệu (0-100)")


class ProductMaterialAssignmentModel(BaseModel):
    product_id: str = Field(..., description="ID của sản phẩm")
    materials: List[MaterialAssignmentItem] = Field(..., min_length=1, description="Danh sách chất liệu")

    @model_validator(mode='after')
    def validate_materials(self):
        material_ids = [m.material_id for m in self.materials]
        if len(material_ids) != len(set(material_ids)):
            raise ValueError('Không được gán trùng material_id')

        total_percentage = sum(m.percentage for m in self.materials)
        if total_percentage > 100:
            raise ValueError(f'Tổng phần trăm vượt quá 100% (hiện tại: {total_percentage}%)')

        return self


class ProductMaterialCreateModel(BaseModel):
    material_id: str
    percentage: float = Field(..., gt=0, le=100, description="Phần trăm từ 0-100")