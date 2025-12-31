import uuid
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import Field, BaseModel, field_validator
import re
from src.schemas.stock import TransactionType, WarehouseRole


class WarehouseCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=1000)
    phone: Optional[str] = Field(None, pattern=r'^(09\d{8}|02\d{9})$')
    email: Optional[str] = None
    manager_id: Optional[str] = Field(None, description="ID của người quản lý kho")
    is_active: bool = True
    is_default: bool = False

    @field_validator('name', 'address')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if v:
            return v.strip()
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if not re.match(r'^(09\d{8}|02\d{9})$', v):
                raise ValueError('Số điện thoại không hợp lệ. Định dạng: 09XXXXXXXX hoặc 02XXXXXXXXX')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip().lower()
        return v


class WarehouseFilterParams(BaseModel):
    search: Optional[str] = Field(None, min_length=1, max_length=255,
                                  description="Tìm kiếm theo tên, mã kho, địa chỉ hoặc tên quản lý")
    is_active: Optional[bool] = Field(None, description="Lọc theo trạng thái hoạt động")
    sort_by: Optional[Literal["created_asc", "created_desc", "name_asc", "name_desc"]] = Field(
        "created_desc",
        description="Sắp xếp theo"
    )

    @field_validator('search')
    @classmethod
    def strip_search(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else None


class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1, max_length=1000)
    phone: Optional[str] = Field(None, pattern=r'^(09\d{8}|02\d{9})$')
    email: Optional[str] = None
    manager_id: Optional[str] = Field(None, description="ID của người quản lý kho. Set null để xóa manager hiện tại")
    remove_manager: bool = Field(False, description="Set true để xóa manager hiện tại")

    @field_validator('name', 'address')
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if not re.match(r'^(09\d{8}|02\d{9})$', v):
                raise ValueError(
                    'Số điện thoại không hợp lệ. '
                    'Định dạng: 09XXXXXXXX hoặc 02XXXXXXXXX'
                )
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v else v

    def has_updates(self) -> bool:
        return any([
            self.name is not None,
            self.address is not None,
            self.phone is not None,
            self.email is not None,
            self.manager_id is not None,
            self.remove_manager
        ])



class AssignManagerModel(BaseModel):
    user_id: str = Field(..., description="ID của nhân viên sẽ trở thành manager")
    new_role_for_old_manager: Optional[WarehouseRole] = Field(
        None,
        description="Vai trò mới cho manager hiện tại (bắt buộc nếu kho đã có manager)"
    )

    @field_validator('new_role_for_old_manager')
    @classmethod
    def validate_new_role(cls, v: Optional[WarehouseRole]) -> Optional[WarehouseRole]:
        if v == WarehouseRole.MANAGER:
            raise ValueError(
                "Không thể gán vai trò MANAGER cho manager cũ. "
                "Chỉ có thể gán các vài trò còn lại."
            )
        return v


class ManagerActivityFilter(BaseModel):
    warehouse_id: Optional[str] = Field(None, description="Lọc theo kho cụ thể")
    transaction_type: Optional[TransactionType] = Field(None, description="Loại giao dịch")
    from_date: Optional[datetime] = Field(None, description="Từ ngày")
    to_date: Optional[datetime] = Field(None, description="Đến ngày")

class AssignStaffItemModel(BaseModel):
    user_id: uuid.UUID = Field(..., description="ID của nhân viên cần assign")
    warehouse_role: WarehouseRole = Field(..., description="Vai trò trong kho")

    @field_validator('warehouse_role')
    @classmethod
    def validate_role(cls, v: WarehouseRole) -> WarehouseRole:
        if v == WarehouseRole.MANAGER:
            raise ValueError(
                "Không thể assign vai trò MANAGER qua function này. "
                "Vui lòng sử dụng function assign-manager riêng."
            )
        return v

class UpdateStaffRoleModel(BaseModel):
    warehouse_role: WarehouseRole = Field(..., description="Vai trò mới")

    @field_validator('warehouse_role')
    @classmethod
    def validate_role(cls, v: WarehouseRole) -> WarehouseRole:
        if v == WarehouseRole.MANAGER:
            raise ValueError(
                "Không thể cập nhật thành MANAGER qua endpoint này. "
                "Vui lòng sử dụng endpoint assign-manager."
            )
        return v

class AssignMultipleStaffModel(BaseModel):
    staff_list: List[AssignStaffItemModel] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Danh sách nhân viên cần assign (tối đa 100)"
    )

    @field_validator('staff_list')
    @classmethod
    def validate_no_duplicates(cls, v: List[AssignStaffItemModel]) -> List[AssignStaffItemModel]:
        user_ids = [staff.user_id for staff in v]
        if len(user_ids) != len(set(user_ids)):
            duplicates = [uid for uid in user_ids if user_ids.count(uid) > 1]
            raise ValueError(
                f"Có user_id bị trùng lặp trong danh sách: {list(set(duplicates))}"
            )
        return v
