from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import List

from src.schemas.stock import WarehouseRole


class UserModel(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    password: str = Field(exclude=True)
    phone: Optional[str]
    customer_status: str = Field(default="active")
    created_at: datetime = Field(default=datetime.now)
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]
    is_verified: bool = Field(default=False)
    is_admin: bool = Field(default=False)
    is_customer: bool = Field(default=False)
    two_fa_secret: Optional[str]
    two_fa_enabled: bool = Field(default=False)

class UserCreateModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class UserUpdateModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class UserReadModel(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str

class UserLoginModel(BaseModel):
    email: str
    password: str

class LoginAdminModel(BaseModel):
    email: str
    password: str

class Setup2FA(BaseModel):
    token: str

class VerifyLoginAdminModel(BaseModel):
    token: str
    otp: str

class ChangePasswordModel(BaseModel):
    old_password: str = Field(
        ...,
        min_length=1,
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
    )
    confirm_new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
    )

class VerifyOTPModel(BaseModel):
    otp: str
    email: str

class UserDeleteModel(BaseModel):
    user_ids: List[str]

class CustomerStatusType:
    ACTIVE = "active"
    INACTIVE = "inactive"
    
class UserRole(str, Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"
    
class AdminStaffRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    
class ResetMethod(str, Enum):
    EMAIL = "email"
    OTP = "otp"

class SortOrder(str, Enum):
    NEWEST = "newest"
    OLDEST = "oldest"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class FilterUserInputModel(BaseModel):
    search: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[UserStatus] = None
    is_verified: Optional[bool] = None
    sort_by_created_at: Optional[SortOrder] = None
    warehouse_code: Optional[str] = None
    warehouse_role: Optional[WarehouseRole] = None

class AdminUpdateModel(BaseModel):
    status: Optional[UserStatus] = Field(default=UserStatus.ACTIVE)
    
class ForgotPasswordConfirmModel(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    new_password_confirm: str = Field(..., min_length=8, max_length=100)


class PasswordResetEmailModel(BaseModel):
    email: str
    check: ResetMethod
    
class VerifyOtpModel(BaseModel):
    email: str
    otp: str = Field(..., min_length=6, max_length=6)

class StaffMultipleDeleteModel(BaseModel):
    user_ids: List[str]
    



