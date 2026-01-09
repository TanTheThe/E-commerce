from sqlmodel import or_
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import User
from src.errors.authentication import AuthException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository

user_repository = UserRepository()
warehouse_repository = WareHouseRepository()


class GetProfileService:
    async def get_profile_customer(self, user_id: str, session: AsyncSession):
        conditions = [
            User.id == user_id,
            User.deleted_at.is_(None),
            User.is_customer == True
        ]
        user = await user_repository.get_user(
            session=session,
            where_conditions=conditions
        )

        if not user:
            AuthException.user_not_found()

        formatted_user = {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "phone": user.phone,
            "is_verified": user.is_verified,
            "customer_status": user.customer_status,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

        return formatted_user

    async def get_profile_admin_staff(self, user_id: str, session: AsyncSession):
        conditions = [
            User.id == user_id,
            User.deleted_at.is_(None),
            or_(User.is_admin == True, User.is_staff == True)
        ]

        user = await user_repository.get_user(session=session, where_conditions=conditions)

        if not user:
            AuthException.user_not_found()

        if not user.is_admin and not user.is_staff:
            AuthException.unauthorized()

        role = "admin" if user.is_admin else "staff"

        formatted_user = {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "role": role,
            "is_verified": user.is_verified
        }

        if user.is_staff and not user.is_admin:
            formatted_user.update({
                "staff_status": user.staff_status,
                "warehouse_id": str(user.warehouse_id) if user.warehouse_id else None,
                "warehouse_role": user.warehouse_role
            })

        return formatted_user



