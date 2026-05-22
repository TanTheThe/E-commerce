from typing import List
from fastapi.security import HTTPBearer
from fastapi import Request, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from starlette import status
from fastapi.exceptions import HTTPException
from src.crud.authentication.utils import decode_token
from src.crud.user.repositories import UserRepository
from src.crud.user.services.get_profile_customer import GetProfileService
from src.database.main import get_session
from src.database.models import User, Permission, UserRole, Role, RolePermission
from src.database.redis import token_in_blocklist
from src.cache.cache_service import CacheService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.user import UserException

PERMISSION_CACHE_TTL = 60 * 5  # 5 phút

get_profile_service = GetProfileService()
user_repository = UserRepository()

def _permission_cache_key(user_id: str) -> str:
    return f"user_permissions:{user_id}"

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token không hợp lệ hoặc đã hết hạn"
            )

        in_blocklist = await token_in_blocklist(token_data['jti'], request)

        if in_blocklist:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token này đã hết hạn hoặc không còn hợp lệ"
            )

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data):
        raise NotImplementedError("Hãy override phương thức này ở class con")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hãy cung cấp access token",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hãy cung cấp refresh token",
            )


def verify_token_and_get_role(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header bị thiếu hoặc không hợp lệ"
        )

    token = auth_header.split(" ")[1]
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token hết hạn hoặc không hợp lệ"
        )

    role = payload.get("role")
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vai trò không tìm thấy trong token"
        )

    return role


async def admin_role_middleware(role: str = Depends(verify_token_and_get_role)):
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ có admin mới có thể sử dụng tính năng này")


async def customer_role_middleware(role: str = Depends(verify_token_and_get_role)):
    if role != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ có customer mới có thể sử dụng tính năng này")


async def staff_role_middleware(role: str = Depends(verify_token_and_get_role)):
    if role != "staff":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ có staff mới có thể sử dụng tính năng này")


access_token_bearer = AccessTokenBearer()
cache_service = CacheService()

async def fetch_user_permissions(session: AsyncSession, user_id: str) -> List[str]:
    conditions = [
        User.id == user_id,
        UserRole.is_active == True,
        Role.is_active == True,
        Role.deleted_at == None,
        Permission.is_active == True,
        Permission.deleted_at == None,
    ]

    result = await user_repository.get_user(
        session=session,
        select_columns=[Permission.code],
        joins=[
            (
                UserRole,
                {
                    "on": UserRole.user_id == User.id
                }
            ),
            (
                Role,
                {
                    "on": Role.id == UserRole.role_id
                }
            ),
            (
                RolePermission,
                {
                    "on": RolePermission.role_id == Role.id
                }
            ),
            (
                Permission,
                {
                    "on": Permission.id == RolePermission.permission_id
                }
            )
        ],
        where_conditions=conditions
    )

    return [permission for permission in result] if result else []

async def get_current_user(token_details: dict = Depends(access_token_bearer),
                           session: AsyncSession = Depends(get_session)) -> User:
    user_id = token_details['user']['id']
    if not user_id:
        UserException.token_invalid()

    user = await user_repository.get_user(
        session=session,
        where_conditions=[
            User.id == user_id,
            User.deleted_at.is_(None)
        ]
    )

    if user is None or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại",
        )

    if user.is_staff and user.staff_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản nhân viên đã bị khóa",
        )

    if not user.is_staff and not user.is_admin and user.customer_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa",
        )

    return user


async def get_current_user_with_permissions(current_user: User = Depends(get_current_user),
                                            session: AsyncSession = Depends(get_session)) -> tuple[User, List[str]]:
    if current_user.is_admin:
        return current_user, ["*"]

    cache_key = _permission_cache_key(str(current_user.id))

    permissions = await cache_service.get_or_set(
        key=cache_key,
        factory_func=fetch_user_permissions,
        ttl=PERMISSION_CACHE_TTL,
        # args truyền vào factory_func
        session=session,
        user_id=str(current_user.id),
    )

    if permissions is None:
        permissions = []

    return current_user, permissions


async def invalidate_user_permission_cache(user_id: str) -> None:
    """
    Gọi hàm này bất cứ khi nào admin:
    - Gán role mới cho user
    - Thu hồi role của user
    - Thay đổi permission của role
    """
    await cache_service.delete(_permission_cache_key(user_id))


def has_permission(*required_permissions: str, require_all: bool = False):
    """
    Factory tạo ra Dependency check permission.

    Args:
        *required_permissions: Các permission code cần kiểm tra.
        require_all:
            False (default) → có ÍT NHẤT 1 là đủ (OR)
            True            → phải có TẤT CẢ (AND)

    Usage:
        # Chỉ cần 1 permission, không cần lấy user trong handler
        @router.get(
            "/orders",
            dependencies=[Depends(has_permission("order:view"))]
        )

        # Cần lấy user + permissions trong handler
        @router.post("/orders/{id}/cancel")
        async def cancel_order(
            order_id: uuid.UUID,
            auth: tuple = Depends(
                has_permission("order:view", "order:approve_cancel", require_all=True)
            )
        ):
            user, permissions = auth
    """

    async def _check(
        auth: tuple[User, List[str]] = Depends(get_current_user_with_permissions),
    ) -> tuple[User, List[str]]:
        user, user_permissions = auth

        # Admin bypass
        if "*" in user_permissions:
            return auth

        required = set(required_permissions)
        granted = set(user_permissions)

        if require_all:
            missing = required - granted
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Không có quyền: {', '.join(missing)}",
                )
        else:
            if not required.intersection(granted):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Không có quyền thực hiện hành động này",
                )

        return auth

    return _check

RequireAuth = Depends(get_current_user)

async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền thực hiện",
        )
    return current_user

RequireAdmin = Depends(require_admin)

async def require_staff(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_staff and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ nhân viên mới có quyền thực hiện",
        )
    return current_user

RequireStaff = Depends(require_staff)

async def require_customer(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_customer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ khách hàng mới có quyền thực hiện",
        )
    return current_user

RequireCustomer = Depends(require_customer)
