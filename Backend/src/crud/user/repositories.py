from datetime import datetime
from typing import Optional
from sqlalchemy.orm import noload
from fastapi import HTTPException, status
from sqlalchemy import ColumnElement
from src.database.models import User
from src.crud.authentication.utils import generate_password_hash
from sqlmodel import select, desc, update, func, or_, distinct
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import and_
from src.schemas.user import UserDeleteModel, FilterUserInputModel


class UserRepository:
    async def get_user(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        base_condition = User.deleted_at.is_(None)

        if conditions is not None:
            combined_condition = and_(base_condition, conditions)
        else:
            combined_condition = base_condition

        statement = select(User).options(
            *joins if joins else []
        ).where(combined_condition)
        result = await session.exec(statement)

        return result.first()


    async def get_all_user(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, order_by: list = None, skip: int = 0, limit: int = 10,
                           joins: list = None):
        count_stmt = select(func.count(User.id)).select_from(User).where(conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(User).options(
            *joins if joins else []
        ).where(conditions)

        if order_by:
            statement = statement.order_by(*order_by, User.id)
        else:
            statement = statement.order_by(User.id)

        statement = statement.offset(skip).limit(limit)
        result = await session.exec(statement)
        users = result.all()

        return users, total


    async def update_user(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()

        return data_need_update


    async def create_user(self, user_data, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        user_data_dict['password'] = generate_password_hash(user_data_dict['password'])

        new_user = User(
            **user_data_dict,
            customer_status="active",
            created_at=datetime.now()
        )
        session.add(new_user)
        await session.commit()

        return new_user

    async def delete_user(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        joins = [
            noload(User.address),
            noload(User.evaluate),
            noload(User.order)
        ]
        user_to_delete = await self.get_user(condition, session, joins)

        if user_to_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Không tìm thấy người dùng.",
                    "error_code": "product_006",
                },
            )
        user_to_delete.deleted_at = datetime.now()
        await session.commit()

        return str(user_to_delete.id)

    async def delete_multiple_user(self, data: UserDeleteModel, session: AsyncSession):
        condition = and_(User.id.in_(data.user_ids), User.deleted_at.is_(None))
        joins = [
            noload(User.address),
            noload(User.evaluate),
            noload(User.order)
        ]
        users = await self.get_all_user(condition, session, None, 0, 1000, joins)
        existing_ids = {str(row.id) for row in users}
        missing_ids = set(data.user_ids) - existing_ids
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không tìm thấy các mã người dùng: {list(missing_ids)}"
            )
        stmt = update(User).where(User.id.in_(data.user_ids)).values(deleted_at=datetime.now())
        await session.exec(stmt)
        await session.commit()

        return data.user_ids

    async def change_status_user(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        joins = [
            noload(User.address),
            noload(User.evaluate),
            noload(User.order)
        ]
        user_to_block = await self.get_user(condition, session)

        if user_to_block is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Không tìm thấy người dùng.",
                    "error_code": "product_006",
                },
            )
        if user_to_block.customer_status == "active":
            user_to_block.customer_status = "inactive"
        else:
            user_to_block.customer_status = "active"

        await session.commit()

        return {
            "id": str(user_to_block.id),
            "new_status": user_to_block.customer_status
        }