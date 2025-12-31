from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
import re


class TagSortEnum(str, Enum):
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"


class TagDeleteStrategy(str, Enum):
    SOFT_DELETE = "soft_delete"
    FORCE_DELETE = "force_delete"
    REJECT = "reject"


class TagQueryParams(BaseModel):
    search: Optional[str] = Field(None, max_length=100, description="Tìm kiếm theo tên tag")

    @field_validator('search')
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if any(char in v for char in ['%', '_', '\\']):
                v = v.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            return v if v else None
        return None


class TagAdminQueryParams(TagQueryParams):
    is_active: Optional[bool] = None
    sort_by: TagSortEnum = Field(TagSortEnum.CREATED_DESC, description="Sắp xếp theo")


class TagCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tên tag")
    is_active: bool = True
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        
        if not v:
            raise ValueError("Tên tag không được để trống")
        
        if not re.match(r'^[\w\s\-àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]+$', v):
            raise ValueError("Tên tag chỉ được chứa chữ cái, số, dấu gạch ngang và khoảng trắng")
        
        return v


class TagUpdateModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Tên tag mới")
    is_active: Optional[bool] = Field(None, description="Trạng thái active")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        v = v.strip()

        if not v:
            raise ValueError("Tên tag không được để trống")

        if not re.match(
                r'^[\w\s\-àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]+$',
                v):
            raise ValueError("Tên tag chỉ được chứa chữ cái, số, dấu gạch ngang và khoảng trắng")

        return v

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        if self.name is None and self.is_active is None:
            raise ValueError("Phải cung cấp ít nhất một trường để cập nhật (name hoặc is_active)")
        return self


class DeleteMultipleTagsModel(BaseModel):
    tag_ids: List[str] = Field(..., min_length=1, max_length=100, description="Danh sách tag IDs cần xóa")
    strategy: TagDeleteStrategy = Field(
        TagDeleteStrategy.SOFT_DELETE,
        description="Chiến lược xóa: soft_delete, force_delete, hoặc reject"
    )

    @field_validator('tag_ids')
    @classmethod
    def validate_tag_ids(cls, v: List[str]) -> List[str]:
        if len(v) != len(set(v)):
            raise ValueError("Danh sách tag_ids không được chứa phần tử trùng lặp")

        return v


class ProductTagAssignmentModel(BaseModel):
    product_id: str = Field(..., description="ID của sản phẩm")
    tag_ids: List[str] = Field(..., min_length=0, max_length=50, description="Danh sách tag IDs")
    
    @field_validator('tag_ids')
    @classmethod
    def validate_tag_ids(cls, v: List[str]) -> List[str]:
        if not v:
            return v
        
        if len(v) != len(set(v)):
            raise ValueError("Danh sách tag_ids không được chứa phần tử trùng lặp")
        
        return v


class TagType(str, Enum):
    SUMMER = "Mùa hè"
    WINTER = "Mùa đông"
    SPRING = "Mùa xuân"
    AUTUMN_FALL = "Mùa thu"
    HOT_TREND = "Xu hướng nóng"
    CASUAL = "Thường ngày"
    FORMAL = "Trang trọng"
    OFFICE_WEAR = "Đồ công sở"
    STREETWEAR = "Streetwear"
    VINTAGE = "Vintage"
    MINIMALIST = "Tối giản"
    SPORTY = "Thể thao"
    OVERSIZED = "Oversize"
    UNISEX = "Unisex"
    PARTY = "Tiệc"
    BACK_TO_SCHOOL = "Trở lại trường học"
    TRAVEL_OUTFIT = "Trang phục du lịch"
    HOLIDAY_VIBES = "Không khí ngày lễ"
    NEW_ARRIVAL = "Hàng mới về"
    BEST_SELLER = "Bán chạy"
    LIMITED_EDITION = "Phiên bản giới hạn"
