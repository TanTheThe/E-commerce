from typing import List, Dict, Any
from sqlalchemy.orm import selectinload
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import User, Warehouse
from src.schemas.user import FilterUserInputModel, UserRole, SortOrder
from sqlmodel import or_, func, desc, asc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository

user_repository = UserRepository()
warehouse_repository = WareHouseRepository()


class GetAllUsersService:
    async def get_all_users(self, filter_data: FilterUserInputModel, user_type: UserRole, session: AsyncSession,
                                    skip: int = 0, limit: int = 10):
        filters = await self.build_filters(filter_data, user_type)

        order_by = self.build_order_by(filter_data)

        joins = []
        options = []
        need_warehouse = (
                user_type == UserRole.STAFF or
                filter_data.warehouse_code is not None or
                filter_data.warehouse_role is not None
        )

        if need_warehouse:
            joins = [
                (
                    Warehouse,
                    {
                        "on": User.warehouse_id == Warehouse.id,
                        "type": "inner"
                    }
                )
            ]
            options = [selectinload(User.warehouse)]

        users, total = await user_repository.get_all_users(
            session=session,
            where_conditions=filters,
            options=options,
            order_by=order_by,
            skip=skip,
            limit=limit,
            joins=joins,
        )

        formatted_users = self.format_users(users, user_type)

        return {
            "data": formatted_users,
            "total": total
        }


    async def build_filters(self, filter_data: FilterUserInputModel, user_type: UserRole) -> List:
        filters = [User.deleted_at.is_(None)]

        if user_type == UserRole.CUSTOMER:
            filters.append(User.is_customer == True)
        elif user_type == UserRole.STAFF:
            filters.append(User.is_staff == True)

        if filter_data.email:
            filters.append(User.email == filter_data.email)

        if filter_data.phone:
            filters.append(User.phone == filter_data.phone)

        if filter_data.is_verified is not None:
            filters.append(User.is_verified == filter_data.is_verified)

        if filter_data.status:
            if user_type == UserRole.CUSTOMER:
                filters.append(User.customer_status == filter_data.status.value)
            elif user_type == UserRole.STAFF:
                filters.append(User.staff_status == filter_data.status.value)

        if filter_data.warehouse_role:
            filters.append(User.warehouse_role == filter_data.warehouse_role.value)

        if filter_data.warehouse_code:
            filters.append(Warehouse.code == filter_data.warehouse_code)

        if filter_data.search:
            search_term = f"%{filter_data.search}%"
            filters.append(or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                func.concat(User.first_name, ' ', User.last_name).ilike(search_term),
                User.email.ilike(search_term)
            ))

        return filters


    def build_order_by(self, filter_data: FilterUserInputModel) -> List:
        if filter_data.sort_by_created_at == SortOrder.NEWEST:
            return [desc(User.created_at)]
        elif filter_data.sort_by_created_at == SortOrder.OLDEST:
            return [asc(User.created_at)]

        return [desc(User.created_at)]


    def format_users(self, users: List, user_type: UserRole) -> List[Dict[str, Any]]:
        formatted_users = []

        for user in users:
            user_data = {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }

            if user_type == UserRole.CUSTOMER:
                user_data["customer_status"] = user.customer_status
            elif user_type == UserRole.STAFF:
                user_data["staff_status"] = user.staff_status
                user_data["warehouse_role"] = user.warehouse_role
                user_data["warehouse_id"] = str(user.warehouse_id)
                user_data["warehouse_code"] = user.warehouse.code if user.warehouse else None,

            formatted_users.append(user_data)

        return formatted_users