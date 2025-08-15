from typing import Optional
from sqlalchemy import ColumnElement
from src.database.models import Address
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, and_
from datetime import datetime
from src.errors.address import AddressException


class AddressRepository:
    async def create_address(self, user_id, address_data, session: AsyncSession):
        address_data_dict = address_data.model_dump()

        new_address = Address(
            **address_data_dict,
            user_id=user_id,
            created_at=datetime.now()
        )
        session.add(new_address)
        await session.commit()

        return new_address


    async def get_all_address(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        statement = select(Address).order_by(desc(Address.created_at))

        if conditions is None:
            conditions = and_(Address.deleted_at == None)
        else:
            conditions = and_(conditions, Address.deleted_at == None)

        statement = statement.where(conditions)
        result = await session.exec(statement)

        return result.all()


    async def get_address(self, conditions: ColumnElement[bool], session: AsyncSession, joins: list = None):
        statement = select(Address).where(conditions).options(*joins if joins else [])

        result = await session.exec(statement)

        return result.first()


    async def update_address(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()

        return data_need_update


    async def delete_address(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        address_to_delete = await self.get_address(condition, session)

        if address_to_delete is None:
            AddressException.not_found_to_delete()

        address_to_delete.deleted_at = datetime.now()
        await session.commit()

        return {}



