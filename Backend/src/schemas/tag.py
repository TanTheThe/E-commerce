from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class TagCreateModel(BaseModel):
    name: str
    is_active: bool = True

class TagUpdateModel(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class DeleteMultipleTagsModel(BaseModel):
    tag_ids: List[str]

class ProductTagAssignmentModel(BaseModel):
    product_id: str
    tag_ids: List[str]

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
