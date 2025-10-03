import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import Field, BaseModel

from src.schemas.stock import TransactionType, WarehouseRole


class WarehouseCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1)
    phone: Optional[str] = Field(None, pattern=r'^(09\d{8}|02\d{9})$')
    email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    manager_id: Optional[uuid.UUID] = Field(None, description="ID của người quản lý kho")
    is_active: bool = True
    is_default: bool = False

class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1)
    phone: Optional[str] = Field(None, pattern=r'^(09\d{8}|02\d{9})$')  # 10 số bắt đầu 09 hoặc 11 số bắt đầu 02
    email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    manager_id: Optional[uuid.UUID] = Field(None, description="ID của người quản lý kho")

class AssignManagerModel(BaseModel):
    user_id: str
    new_role_for_old_manager: WarehouseRole

class ManagerActivityFilter(BaseModel):
    warehouse_id: Optional[str] = Field(None, description="Lọc theo kho cụ thể")
    transaction_type: Optional[TransactionType] = Field(None, description="Loại giao dịch")
    from_date: Optional[datetime] = Field(None, description="Từ ngày")
    to_date: Optional[datetime] = Field(None, description="Đến ngày")

class AssignStaffItemModel(BaseModel):
    user_id: str
    warehouse_role: WarehouseRole

class UpdateStaffRoleModel(BaseModel):
    warehouse_role: WarehouseRole

class AssignMultipleStaffModel(BaseModel):
    staff_list: List[AssignStaffItemModel]
