from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re
from typing import List
from src.schemas.stock import WarehouseRole


EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

class UserCreateModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Tên không được để trống")

        v = v.strip()

        if len(v) > 50:
            raise ValueError("Tên không được vượt quá 50 ký tự")

        if '  ' in v:
            raise ValueError("Tên không được chứa khoảng trắng thừa")

        if not re.match(r"^[a-zA-ZÀ-ỿ0-9\s\-',.]+$", v):
            raise ValueError("Tên chứa ký tự không hợp lệ")

        words = v.split()
        if len(words) > 5:
            raise ValueError("Tên quá dài (tối đa 5 từ)")

        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email không được để trống")

        email = v.strip().lower()

        if len(email) > 255:
            raise ValueError("Email quá dài (tối đa 255 ký tự)")

        if not re.match(EMAIL_REGEX, email):
            raise ValueError("Định dạng email không hợp lệ")

        return email

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Mật khẩu mới không được để trống")

        if v != v.strip():
            raise ValueError("Mật khẩu mới không được có khoảng trắng ở đầu hoặc cuối")

        if ' ' in v:
            raise ValueError("Mật khẩu mới không được chứa khoảng trắng")

        if len(v) < 8:
            raise ValueError("Mật khẩu mới phải có ít nhất 8 ký tự")

        if len(v) > 128:
            raise ValueError("Mật khẩu mới không được vượt quá 128 ký tự")

        if not any(c.isupper() for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ hoa")

        if not any(c.islower() for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ thường")

        if not any(c.isdigit() for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ số")

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 ký tự đặc biệt: !@#$%^&*()_+-=[]{}|;:,.<>?")

        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?')
        if not all(c in allowed_chars for c in v):
            raise ValueError("Mật khẩu chứa ký tự không hợp lệ")

        common_patterns = [
            'password', 'qwerty', 'abc123', '111111', '123123',
            'admin', 'letmein', '12345', '123456'
        ]
        if any(pattern in v.lower() for pattern in common_patterns):
            raise ValueError("Mật khẩu chứa các mẫu phổ biến không an toàn")

        if any(v[i:i + 5] == v[i] * 5 for i in range(len(v) - 4)):
            raise ValueError("Mật khẩu không được chứa quá 5 ký tự giống nhau liên tiếp")

        return v


class UserUpdateModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()

            if not v:
                raise ValueError('Tên không được để trống')

            if len(v) > 50:
                raise ValueError('Tên không được vượt quá 50 ký tự')

            if '  ' in v:
                raise ValueError('Tên không được chứa khoảng trắng liên tiếp')

            if not re.match(r'^[a-zA-ZÀ-ỹ\s]+$', v):
                raise ValueError('Tên chỉ được chứa chữ cái và khoảng trắng')

        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()

            if not v:
                raise ValueError('Số điện thoại không được để trống')

            v = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

            if not v.isdigit():
                raise ValueError('Số điện thoại chỉ được chứa chữ số')

            if len(v) < 9 or len(v) > 20:
                raise ValueError('Số điện thoại phải có từ 9-20 chữ số')

        return v


class UserLoginModel(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email không được để trống")

        email = v.strip().lower()

        if len(email) > 255:
            raise ValueError("Email quá dài (tối đa 255 ký tự)")

        if not re.match(EMAIL_REGEX, email):
            raise ValueError("Định dạng email không hợp lệ")

        return email

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Password không được để trống")

        if len(v) < 8:
            raise ValueError("Password phải có ít nhất 8 ký tự")

        if len(v) > 128:
            raise ValueError("Password không được quá 128 ký tự")

        return v


class Setup2FA(BaseModel):
    token: str

    @field_validator('token')
    @classmethod
    def validate_token(cls, v):
        if not v or not v.strip():
            raise ValueError('Token không được để trống')

        if len(v) > 500:
            raise ValueError('Token không hợp lệ')

        if any(char in v for char in ['\n', '\r', '\0']):
            raise ValueError('Token chứa ký tự không hợp lệ')

        return v.strip()

class VerifyLoginAdminModel(BaseModel):
    token: str
    otp: str

    @field_validator('token')
    @classmethod
    def validate_token(cls, v):
        if not v or not v.strip():
            raise ValueError('Token không được để trống')

        if len(v) > 500:
            raise ValueError('Token không hợp lệ')

        if any(char in v for char in ['\n', '\r', '\0']):
            raise ValueError('Token chứa ký tự không hợp lệ')

        return v.strip()

    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v):
        if not v or not v.strip():
            raise ValueError('Mã OTP không được để trống')

        if not re.match(r'^\d{6}$', v.strip()):
            raise ValueError('Mã OTP phải là 6 chữ số')

        return v.strip()


class ChangePasswordModel(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str

    @field_validator('old_password')
    @classmethod
    def validate_old_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Mật khẩu cũ không được để trống")

        return v

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Mật khẩu mới không được để trống")

        if v != v.strip():
            raise ValueError("Mật khẩu mới không được có khoảng trắng ở đầu hoặc cuối")

        if ' ' in v:
            raise ValueError("Mật khẩu mới không được chứa khoảng trắng")

        if len(v) < 8:
            raise ValueError("Mật khẩu mới phải có ít nhất 8 ký tự")

        if len(v) > 100:
            raise ValueError("Mật khẩu mới không được vượt quá 100 ký tự")

        if not any(c.isupper() for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ hoa")

        if not any(c.islower() for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ thường")

        if not any(c.isdigit() for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ số")

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 ký tự đặc biệt: !@#$%^&*()_+-=[]{}|;:,.<>?")

        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?')
        if not all(c in allowed_chars for c in v):
            raise ValueError("Mật khẩu chứa ký tự không hợp lệ")

        common_patterns = [
            'password', 'qwerty', 'abc123', '111111', '123123',
            'admin', 'letmein', '12345', '123456'
        ]
        if any(pattern in v.lower() for pattern in common_patterns):
            raise ValueError("Mật khẩu chứa các mẫu phổ biến không an toàn")

        if any(v[i:i + 5] == v[i] * 5 for i in range(len(v) - 4)):
            raise ValueError("Mật khẩu không được chứa quá 5 ký tự giống nhau liên tiếp")

        return v

    @field_validator('confirm_new_password')
    @classmethod
    def validate_confirm_password(cls, v, values) -> str:
        if not v or not v.strip():
            raise ValueError("Xác nhận mật khẩu không được để trống")

        if v != v.strip():
            raise ValueError("Xác nhận mật khẩu không được có khoảng trắng ở đầu hoặc cuối")

        if len(v) < 8:
            raise ValueError("Xác nhận mật khẩu phải có ít nhất 8 ký tự")

        if len(v) > 100:
            raise ValueError("Xác nhận mật khẩu không được vượt quá 100 ký tự")

        return v

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("Mật khẩu mới và xác nhận mật khẩu không khớp")
        return self


class VerifyOTPModel(BaseModel):
    otp: str
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email không được để trống")

        email = v.strip().lower()

        if len(email) > 255:
            raise ValueError("Email quá dài (tối đa 255 ký tự)")

        if not re.match(EMAIL_REGEX, email):
            raise ValueError("Định dạng email không hợp lệ")

        return email

    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError('Mã OTP không được để trống')

        if len(v) != 6:
            raise ValueError('Mã OTP phải gồm đúng 6 ký tự')

        if not v.isdigit():
            raise ValueError('Mã OTP chỉ được chứa chữ số')

        return v


class UserDeleteModel(BaseModel):
    user_ids: List[str]

    @field_validator('user_ids')
    @classmethod
    def validate_user_ids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError('Danh sách user_ids không được trống')

        if len(v) > 100:
            raise ValueError('Danh sách user_ids không được vượt quá 100 phần tử')

        if len(v) != len(set(v)):
            raise ValueError('Danh sách user_ids không được chứa ID trùng lặp')

        return v

    
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


class ForgotPasswordConfirmModel(BaseModel):
    token: str
    new_password: str
    new_password_confirm: str

    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Token không hợp lệ')
        if len(v.strip()) > 500:
            raise ValueError('Token không hợp lệ')
        return v.strip()

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Mật khẩu mới không được để trống")

        if v != v.strip():
            raise ValueError("Mật khẩu mới không được có khoảng trắng ở đầu hoặc cuối")

        if ' ' in v:
            raise ValueError("Mật khẩu mới không được chứa khoảng trắng")

        if len(v) < 8:
            raise ValueError("Mật khẩu mới phải có ít nhất 8 ký tự")

        if len(v) > 100:
            raise ValueError("Mật khẩu mới không được vượt quá 100 ký tự")

        if not any(c.isupper() for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ hoa")

        if not any(c.islower() for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ thường")

        if not any(c.isdigit() for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ số")

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 ký tự đặc biệt: !@#$%^&*()_+-=[]{}|;:,.<>?")

        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?')
        if not all(c in allowed_chars for c in v):
            raise ValueError("Mật khẩu chứa ký tự không hợp lệ")

        common_patterns = [
            'password', 'qwerty', 'abc123', '111111', '123123',
            'admin', 'letmein', '12345', '123456'
        ]
        if any(pattern in v.lower() for pattern in common_patterns):
            raise ValueError("Mật khẩu chứa các mẫu phổ biến không an toàn")

        if any(v[i:i + 5] == v[i] * 5 for i in range(len(v) - 4)):
            raise ValueError("Mật khẩu không được chứa quá 5 ký tự giống nhau liên tiếp")

        return v

    @field_validator('new_password_confirm')
    @classmethod
    def validate_confirm_password(cls, v, values) -> str:
        if not v or not v.strip():
            raise ValueError("Xác nhận mật khẩu không được để trống")

        if v != v.strip():
            raise ValueError("Xác nhận mật khẩu không được có khoảng trắng ở đầu hoặc cuối")

        if len(v) < 8:
            raise ValueError("Xác nhận mật khẩu phải có ít nhất 8 ký tự")

        if len(v) > 100:
            raise ValueError("Xác nhận mật khẩu không được vượt quá 100 ký tự")

        return v


class FilterUserInputModel(BaseModel):
    search: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[UserStatus] = None
    is_verified: Optional[bool] = None
    sort_by_created_at: Optional[SortOrder] = None
    warehouse_code: Optional[str] = None
    warehouse_role: Optional[WarehouseRole] = None

    @field_validator('search', 'warehouse_code')
    @classmethod
    def strip_and_validate_short(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 100:
                raise ValueError('Giá trị không được vượt quá 100 ký tự')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if len(v) > 255:
                raise ValueError('Email không được vượt quá 255 ký tự')
            if '@' not in v or '.' not in v.split('@')[-1]:
                raise ValueError('Email không hợp lệ')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if len(v) > 20:
                raise ValueError('Số điện thoại không được vượt quá 20 ký tự')
            if not v.isdigit() or len(v) < 9 or len(v) > 15:
                raise ValueError('Số điện thoại không hợp lệ')
        return v


class PasswordResetEmailModel(BaseModel):
    email: str
    check: ResetMethod

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email không được để trống")

        email = v.strip().lower()

        if len(email) > 255:
            raise ValueError("Email quá dài (tối đa 255 ký tự)")

        if not re.match(EMAIL_REGEX, email):
            raise ValueError("Định dạng email không hợp lệ")

        return email


class StaffMultipleDeleteModel(BaseModel):
    user_ids: List[str]

    @field_validator('user_ids')
    @classmethod
    def validate_user_ids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError('Danh sách user_ids không được trống')

        if len(v) > 100:
            raise ValueError('Danh sách user_ids không được vượt quá 100 phần tử')

        duplicates = list(set(uid for uid in v if v.count(uid) > 1))
        if duplicates:
            raise ValueError(f'Có user_id bị trùng lặp trong danh sách: {duplicates}')

        return v



