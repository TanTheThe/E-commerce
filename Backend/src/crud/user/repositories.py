from datetime import datetime
from typing import Any, Dict, Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy import ColumnElement
from src.database.models import User
from src.crud.authentication.utils import generate_password_hash
from sqlmodel import select, update, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import and_

from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.schemas.user import UserCreateModel, UserDeleteModel, UserRole


class UserRepository:
    async def get_user(self, session: AsyncSession,
                       select_columns: Optional[List[Any]] = None,
                       joins: Optional[List[Tuple[Any, dict]]] = None,
                       where_conditions: Optional[List[ColumnElement[bool]]] = None,
                       group_by_columns: Optional[List[Any]] = None,
                       having_conditions: Optional[List[ColumnElement[bool]]] = None,
                       order_by: Optional[Any] = None,
                       options: Optional[List[Any]] = None,
                       for_update: Optional[bool] = False):

        if select_columns is None:
            query = select(User)
        else:
            query = select(*select_columns).select_from(User)

        if joins:
            for table, config in joins:
                if config.get('type') == 'outer':
                    query = query.outerjoin(table, config['on'])
                else:
                    query = query.join(table, config['on'])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        if for_update:
            query = query.with_for_update()

        result = await session.exec(query)
        user = result.one_or_none()

        return user


    async def get_all_users(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None):
        if select_columns is None:
            query = select(User)
        else:
            query = select(*select_columns).select_from(User)

        if joins:
            for table, config in joins:
                if config.get('type') == 'outer':
                    query = query.outerjoin(table, config['on'])
                else:
                    query = query.join(table, config['on'])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.exec(count_query)
        total = count_result.one() or 0

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        users = result.all()

        return users, total


    async def update_user(self, where_conditions: Optional[List[ColumnElement[bool]]],
                             update_data: Dict[str, Any], session: AsyncSession):
        query = (
            update(User)
            .where(and_(*where_conditions))
            .values(**update_data)
            .returning(User)
        )

        result = await session.exec(query)

        return result.one_or_none()


    async def create_user(self, user_data: dict, session: AsyncSession):
        new_user = User(**user_data)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user


    async def delete_user(self, where_conditions: Optional[List[ColumnElement[bool]]], session: AsyncSession):
        user_to_delete = await self.get_user(session=session, where_conditions=where_conditions)

        if user_to_delete is None:
            AuthException.user_not_found()

        user_to_delete.deleted_at = datetime.now()
        await session.commit()

        return str(user_to_delete.id)


    async def delete_multiple_user(self, data: UserDeleteModel, session: AsyncSession):
        conditions = [User.id.in_(data.user_ids), User.deleted_at.is_(None)]
        users = await self.get_all_users(session=session, where_conditions=conditions, skip=0, limit=1000)
        existing_ids = {str(row.id) for row in users}
        missing_ids = set(data.user_ids) - existing_ids
        if missing_ids:
            UserException.not_found_or_deleted(missing_ids)

        stmt = update(User).where(User.id.in_(data.user_ids)).values(deleted_at=datetime.now())
        await session.exec(stmt)
        await session.commit()

        return data.user_ids