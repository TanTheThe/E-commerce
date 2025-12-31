from typing import Optional, List, Dict, Any
from sqlalchemy.orm import selectinload

from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import User, UserSpecialOffer, Warehouse
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.errors.warehouse import WareHouseException
from src.schemas.user import UserDeleteModel, \
    FilterUserInputModel, UserRole, SortOrder
from sqlmodel import and_, or_, func, desc, asc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository

user_repository = UserRepository()
warehouse_repository = WareHouseRepository()


class UserService:
    async def get_detail_admin_service(self, id: str, session: AsyncSession):
        condition = and_(User.id == id)
        joins = [
            selectinload(User.address)
        ]
        user = await user_repository.get_user(condition, session, joins)

        if not user:
            AuthException.user_not_found()

        filtered_user = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
            "is_verified": user.is_verified,
            "customer_status": user.customer_status,
            "is_customer": user.is_customer,
            "two_fa_enabled": user.two_fa_enabled
        }

        return filtered_user

    async def get_all_users_service(self, filter_data: FilterUserInputModel, user_type: UserRole, session: AsyncSession, skip: int = 0,
                                       limit: int = 10):
        filters = await self.build_filters(filter_data, user_type)

        order_by = self.build_order_by(filter_data)

        joins = [(Warehouse, User.warehouse_id == Warehouse.id)]
        options = [selectinload(User.warehouse)]
        users, total = await user_repository.get_all_users(filters, session, skip, limit, order_by=order_by, options=options, joins=joins)

        formatted_users = self.format_users(users, user_type)

        return {
            "data": formatted_users,
            "total": total
        }

    async def build_filters(self, filter_data: FilterUserInputModel, user_type: UserRole) -> List:
        filters = []

        filters.append(User.deleted_at.is_(None))

        if user_type == UserRole.CUSTOMER:
            filters.append(User.is_customer == True)
        elif user_type == UserRole.STAFF:
            filters.append(User.is_staff == True)

        if filter_data.search:
            search_term = f"%{filter_data.search}%"
            full_name_search = func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
            filters.append(or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                full_name_search,
                User.email.ilike(search_term)
            ))

        if filter_data.email:
            filters.append(User.email == filter_data.email.lower())

        if filter_data.phone:
            filters.append(User.phone == filter_data.phone)

        if filter_data.status:
            if user_type == UserRole.CUSTOMER:
                filters.append(User.customer_status == filter_data.status.value)
            elif user_type == UserRole.STAFF:
                filters.append(User.staff_status == filter_data.status.value)

        if filter_data.is_verified is not None:
            filters.append(User.is_verified == filter_data.is_verified)

        if filter_data.warehouse_role:
            filters.append(User.warehouse_role == filter_data.warehouse_role.value)

        if filter_data.warehouse_code:
            filters.append(Warehouse.code == filter_data.warehouse_code)

        return filters

    def build_order_by(self, filter_data: FilterUserInputModel) -> List:
        order_by = []

        if filter_data.sort_by_created_at:
            if filter_data.sort_by_created_at == SortOrder.NEWEST:
                order_by.append(desc(User.created_at))
            else:
                order_by.append(asc(User.created_at))

        if not order_by:
            order_by = [desc(User.created_at)]

        return order_by

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


    async def get_all_customer_for_offer_service(self, offer_id: str, search: Optional[str], session: AsyncSession,
                                                 skip: int = 0, limit: int = 10):
        filters = [
            User.deleted_at.is_(None),
            User.is_customer == True,
            User.customer_status == "active",
            User.is_verified == True
        ]

        if search:
            search = search.strip()
            if search:  # Check not empty after strip
                search_term = f"%{search}%"
                filters.append(or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                    func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
                ))

        subquery = (
            select(UserSpecialOffer.user_id)
            .where(
                UserSpecialOffer.special_offer_id == offer_id,
            )
            .scalar_subquery()
        )
        filters.append(~User.id.in_(subquery))

        order_by = desc(User.created_at)

        users, total = await user_repository.get_all_users(session=session, where_conditions=filters, skip=skip,
                                                           limit=limit, order_by=order_by)

        filtered_users = [
            {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "customer_status": user.customer_status,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ]

        return {
            "data": filtered_users,
            "total": total
        }

    async def get_staffs_by_warehouse_service(self, warehouse_id: str, session: AsyncSession, skip: int = 0,
                                              limit: int = 10):
        conditions = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(conditions, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        filters = [
            User.is_staff == True,
            User.staff_status == "active",
            User.is_verified == True,
            User.warehouse_id == warehouse_id
        ]

        users, total = await user_repository.get_all_users(filters, session, skip=skip, limit=limit, order_by=[User.created_at.desc()])

        formatted_users = []
        for user in users:
            formatted_users.append({
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
            })

        return {
            "data": formatted_users,
            "total": total
        }


    async def delete_user(self, user_id: str, session: AsyncSession):
        condition = and_(User.id == user_id)
        user_delete_id = await user_repository.delete_user(condition, session)
        return user_delete_id

    async def delete_multiple_user(self, data: UserDeleteModel, session: AsyncSession):
        user_ids = await user_repository.delete_multiple_user(data, session)
        return user_ids

    async def change_status_user(self, user_id: str, role: UserRole, session: AsyncSession):
        condition = and_(User.id == user_id, User.deleted_at.is_(None))
        user_block = await user_repository.change_status_user(condition, role, session)
        return user_block

    async def get_profile_customer_service(self, user_id: str, session: AsyncSession):
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

    async def get_profile_admin_staff_service(self, user_id: str, session: AsyncSession):
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

    async def get_available_staffs_service(self, session: AsyncSession, skip: int = 0, limit: int = 10):
        filters = [
            User.is_staff == True,
            User.staff_status == "active",
            User.is_verified == True,
            User.warehouse_id == None,
            User.warehouse_role == None
        ]

        users, total = await user_repository.get_all_users(filters, session, skip=skip, limit=limit, order_by=[User.created_at.desc()])

        formatted_users = []
        for user in users:
            formatted_users.append({
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "is_verified": user.is_verified,
                "staff_status": user.staff_status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            })

        return {
            "data": formatted_users,
            "total": total
        }


    async def update_profile_service(self, user_id: str, update_data, session: AsyncSession):
        conditions = [
            User.id == user_id,
            User.deleted_at.is_(None)
        ]
        user_need_update = await user_repository.get_user(session=session, where_conditions=conditions)

        if not user_need_update:
            AuthException.user_not_found()

        update_dict = update_data.model_dump(exclude_none=True)

        if not update_dict:
            raise ValueError("Không có dữ liệu để cập nhật")

        if 'phone' in update_dict and update_dict['phone'] != user_need_update.phone:
            conditions = [
                User.phone == update_dict['phone'],
                User.id != user_id,
                User.deleted_at.is_(None)
            ]
            _, count = await user_repository.get_all_users(session=session, where_conditions=conditions)
            if count > 0:
                UserException.phone_already_in_use()

        user_after_update = await user_repository.update_user(
            user_need_update,
            update_dict,
            session
        )

        await session.commit()
        await session.refresh(user_after_update)

        return user_after_update

