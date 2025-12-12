from datetime import datetime

from sqlalchemy import ColumnElement

from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import Order
from src.crud.address.repositories import AddressRepository
from src.crud.order.repositories import OrderRepository
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.user.repositories import UserRepository
from src.crud.product.repositories import ProductRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.color.repositories import ColorRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, func, select
from src.errors.order import OrderException

order_repository = OrderRepository()
special_offer_repository = SpecialOfferRepository()
user_repository = UserRepository()
address_repository = AddressRepository()
product_repository = ProductRepository()
order_detail_repository = OrderDetailRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()

COMPLETED_ORDER_STATUSES = ["delivered", "received"]

class StatisticsOrderService:
    async def get_comprehensive_statistics(self, session: AsyncSession, from_date: datetime, to_date: datetime):
        base_condition = and_(
            Order.deleted_at.is_(None),
            Order.created_at >= from_date,
            Order.created_at <= to_date
        )

        completed_condition = and_(
            base_condition,
            Order.status.in_(COMPLETED_ORDER_STATUSES)
        )

        count_orders = await self.count_orders(session, base_condition)
        total_sales = await self.get_total_sales(session, completed_condition)
        total_revenue = await self.get_total_revenue(session, completed_condition)

        avg_order_value = (
            total_revenue / count_orders if count_orders > 0 else 0
        )

        return {
            "count_orders": count_orders,
            "total_sales": float(total_sales),
            "total_revenue": float(total_revenue),
            "average_order_value": round(avg_order_value, 2)
        }

    async def count_orders(self, session: AsyncSession, condition: ColumnElement[bool]):
        statement = select(func.count(Order.id)).where(condition)
        result = await session.exec(statement)
        return result.one() or 0

    async def get_total_sales(self, session: AsyncSession, condition: ColumnElement[bool]):
        statement = select(
            func.coalesce(func.sum(Order.sub_total), 0)
        ).where(condition)

        result = await session.exec(statement)
        return float(result.one() or 0)

    async def get_total_revenue(self, session: AsyncSession, condition: ColumnElement[bool]):
        statement = select(
            func.coalesce(func.sum(Order.total_price), 0)
        ).where(condition)

        result = await session.exec(statement)
        return float(result.one() or 0)

