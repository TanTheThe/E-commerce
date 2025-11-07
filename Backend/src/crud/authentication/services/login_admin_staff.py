from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.schemas.user import UserRole, AdminStaffRole

user_repository = UserRepository()

class LoginAdminStaffService:
    async def find_and_validate_user(self, email: str, role: UserRole, session: AsyncSession):
        condition = [User.email == email, User.deleted_at.is_(None)]
        user = await user_repository.get_user(session=session, where_conditions=condition)

        if not user:
            AuthException.user_not_found()

        if not user.is_verified:
            AuthException.user_not_verified()

        if role == UserRole.ADMIN:
            if not user.is_admin:
                AuthException.unauthorized_admin()
        elif role == UserRole.STAFF:
            if not user.is_staff:
                AuthException.unauthorized_staff()
            if user.staff_status != "active":
                AuthException.staff_account_disabled()
        elif role == UserRole.CUSTOMER:
            if not user.is_customer:
                AuthException.unauthorized_customer()
            if user.customer_status != "active":
                AuthException.customer_account_disabled()

        return user


    async def detect_user_role(self, email: str, allowed_roles: list[UserRole], session: AsyncSession):
        for role in allowed_roles:
            user = await self.find_and_validate_user(email, role, session)
            if user:
                admin_staff_role = (
                    AdminStaffRole.ADMIN if role == UserRole.ADMIN else AdminStaffRole.STAFF
                )
                return admin_staff_role

        UserException.role_invalid()