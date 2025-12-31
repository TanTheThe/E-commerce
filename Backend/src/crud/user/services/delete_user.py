from datetime import datetime
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


class DeleteUserService:
    async def delete_user(self, user_id: str, session: AsyncSession):
        conditions = [
            User.id == user_id,
            User.deleted_at.is_(None)
        ]
        user_to_delete = await user_repository.get_user(
            session=session,
            where_conditions=conditions
        )

        if not user_to_delete:
            AuthException.user_not_found()

        user_to_delete.deleted_at = datetime.now()
        await session.commit()

        return str(user_to_delete.id)


    async def delete_multiple_user(self, data: UserDeleteModel, session: AsyncSession):
        requested_ids = data.user_ids
        requested_count = len(requested_ids)

        conditions = [
            User.id.in_(requested_ids),
            User.deleted_at.is_(None)
        ]

        existing_users, _ = await user_repository.get_all_users(session=session, where_conditions=conditions)
        existing_ids = {str(user_id) for user_id in existing_users}

        missing_ids = set(requested_ids) - existing_ids

        if missing_ids:
            missing_count = len(missing_ids)
            if missing_count <= 5:
                UserException.not_found_or_deleted(missing_ids)
            else:
                sample_ids = ', '.join(list(missing_ids)[:5])
                UserException.not_found_or_deleted_example(missing_count, sample_ids)

        deleted_at = datetime.now()
        await user_repository.update_user(
            where_conditions=User.id.in_(existing_ids),
            update_data={"deleted_at": deleted_at},
            session=session
        )

        await session.commit()

        return {
            "deleted_count": len(existing_ids),
            "requested_count": requested_count,
            "deleted_ids": list(existing_ids),
            "deleted_at": deleted_at.isoformat()
        }