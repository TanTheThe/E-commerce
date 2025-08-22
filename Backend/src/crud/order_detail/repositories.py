from typing import Optional
from sqlalchemy import ColumnElement
from src.database.models import Product, Order_Detail, Order
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, func, and_
from datetime import datetime


class OrderDetailRepository:
    async def create_order_detail(self, order_detail_list, session: AsyncSession):
        new_order_details = []

        for item in order_detail_list:
            if not isinstance(item, dict):
                item_dict = item.model_dump(exclude_none=True)
            else:
                item_dict = item

            new_order_detail = Order_Detail(**item_dict)
            new_order_detail.created_at = datetime.now()
            new_order_details.append(new_order_detail)

        session.add_all(new_order_details)
        await session.flush()

    async def get_order_detail(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession,
                               joins: list = None):
        statement = select(Order_Detail).where(conditions)
        if joins:
            statement = statement.options(*joins)

        result = await session.exec(statement)

        return result.one_or_none()


