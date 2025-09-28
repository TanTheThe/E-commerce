from typing import Optional
from sqlalchemy.orm import selectinload
from src.database.models import User, UserSpecialOffer
from src.errors.authentication import AuthException
from src.schemas.user import UserDeleteModel, \
    FilterUserInputModel
from sqlmodel import and_, or_, func, desc, asc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository

user_repository = UserRepository()


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

    async def get_all_customer_service(self, filter_data: FilterUserInputModel, session: AsyncSession, skip: int = 0,
                                       limit: int = 10):
        filters = [User.deleted_at.is_(None)]

        if filter_data.search:
            search_term = f"%{filter_data.search}%"
            full_name_search = func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
            filters.append(or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                full_name_search
            ))

        if filter_data.email:
            filters.append(User.email == filter_data.email)

        if filter_data.phone:
            filters.append(User.phone == filter_data.phone)

        if filter_data.customer_status:
            filters.append(User.customer_status == filter_data.customer_status)

        order_by = []
        if filter_data.sort_by_created_at:
            if filter_data.sort_by_created_at == "newest":
                order_by.append(desc(User.created_at))
            else:
                order_by.append(asc(User.created_at))

        if not order_by:
            order_by = [desc(User.created_at)]

        condition = and_(*filters) if filters else None
        users, total = await user_repository.get_all_user(condition, session, order_by, skip, limit)

        filtered_users = [
            {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "customer_status": user.customer_status,
                "created_at": str(user.created_at)
            }
            for user in users
        ]

        return {
            "data": filtered_users,
            "total": total
        }


    async def get_all_customer_for_offer_service(self, offer_id: str, search: Optional[str], session: AsyncSession, skip: int = 0,
                                       limit: int = 10):
        filters = [User.deleted_at.is_(None)]

        if search:
            search_term = f"%{search}%"
            full_name_search = func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
            filters.append(or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term),
                full_name_search
            ))

        subquery = (
            select(UserSpecialOffer.user_id)
            .where(UserSpecialOffer.special_offer_id == offer_id)
        )
        filters.append(User.id.notin_(subquery))

        order_by = [desc(User.created_at)]

        condition = and_(*filters) if filters else None
        users, total = await user_repository.get_all_user(condition, session, order_by, skip, limit)

        filtered_users = [
            {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "customer_status": user.customer_status,
                "created_at": str(user.created_at)
            }
            for user in users
        ]

        return {
            "data": filtered_users,
            "total": total
        }

    async def delete_user(self, user_id: str, session: AsyncSession):
        condition = and_(User.id == user_id)
        user_delete_id = await user_repository.delete_user(condition, session)
        return user_delete_id

    async def delete_multiple_user(self, data: UserDeleteModel, session: AsyncSession):
        user_ids = await user_repository.delete_multiple_user(data, session)
        return user_ids

    async def change_status_user(self, user_id: str, session: AsyncSession):
        condition = and_(User.id == user_id)
        user_block = await user_repository.change_status_user(condition, session)
        return user_block

    async def get_profile_customer_service(self, id: str, session: AsyncSession):
        condition = and_(User.id == id)
        user = await user_repository.get_user(condition, session)

        if not user:
            AuthException.user_not_found()

        filtered_user = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone
        }

        return filtered_user

    async def get_profile_admin_service(self, id: str, session: AsyncSession):
        condition = and_(User.id == id)
        user = await user_repository.get_user(condition, session)

        if not user:
            AuthException.user_not_found()

        filtered_user = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone
        }

        return filtered_user

    async def update_profile_service(self, user_id: str, update_data, session: AsyncSession):
        condition = and_(User.id == user_id)
        user_need_update = await user_repository.get_user(condition, session)

        if not user_need_update:
            AuthException.user_not_found()

        user_after_update = await user_repository.update_user(user_need_update, update_data.model_dump(), session)
        await session.commit()

        return user_after_update

