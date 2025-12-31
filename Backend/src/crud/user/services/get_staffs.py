from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import User, Warehouse
from src.errors.warehouse import WareHouseException
from sqlmodel import desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository

user_repository = UserRepository()
warehouse_repository = WareHouseRepository()


class GetStaffsService:
    async def get_staffs_by_warehouse_service(self, warehouse_id: str, session: AsyncSession, skip: int = 0,
                                              limit: int = 10):
        conditions = [
            Warehouse.id == warehouse_id,
            Warehouse.deleted_at.is_(None)
        ]
        warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=conditions)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        filters = [
            User.is_staff == True,
            User.staff_status == "active",
            User.is_verified == True,
            User.warehouse_id == warehouse_id,
            User.deleted_at.is_(None)
        ]

        users, total = await user_repository.get_all_users(session=session, where_conditions=filters, skip=skip,
                                                           limit=limit, order_by=desc(User.created_at))

        formatted_users = [
            {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "is_verified": user.is_verified,
                "staff_status": user.staff_status,
                "warehouse_id": str(user.warehouse_id) if user.warehouse_id else None,
                "warehouse_role": user.warehouse_role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            for user in users
        ]

        return {
            "data": formatted_users,
            "total": total
        }


    async def get_available_staffs_service(self, session: AsyncSession, skip: int = 0, limit: int = 10):
        filters = [
            User.is_staff == True,
            User.staff_status == "active",
            User.is_verified == True,
            User.warehouse_id.is_(None),
            User.warehouse_role.is_(None),
            User.deleted_at.is_(None)
        ]

        users, total = await user_repository.get_all_users(session=session, where_conditions=filters, skip=skip,
                                                           limit=limit, order_by=desc(User.created_at))

        formatted_users = [
            {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "is_verified": user.is_verified,
                "staff_status": user.staff_status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            for user in users
        ]

        return {
            "data": formatted_users,
            "total": total
        }


