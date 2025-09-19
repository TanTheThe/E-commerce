from src.crud.notification.services import NotificationService
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
from sqlmodel import and_, func
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
notification_service = NotificationService()

class StatisticsOrderService:
    async def count_new_orders(self, to_date, from_date, session: AsyncSession):
        condition = and_(Order.created_at >= from_date, Order.created_at <= to_date)
        orders = await order_repository.count_orders(condition, session)

        if orders is None:
            OrderException.not_found()

        return len(orders)

    async def get_total_sales(self, today, seven_days_ago, session: AsyncSession):
        condition = and_(Order.created_at >= seven_days_ago, Order.status.in_(["delivered", "received"]))
        column_expr = func.coalesce(func.sum(Order.sub_total), 0)
        total_sales = await order_repository.get_statistics(column_expr, condition, session)

        if total_sales is None:
            OrderException.fail_get_total_sales()

        return total_sales

    async def get_total_revenue(self, today, seven_days_ago, session: AsyncSession):
        condition = and_(Order.created_at >= seven_days_ago, Order.status.in_(["delivered", "received"]))
        column_expr = func.coalesce(func.sum(Order.total_price), 0)
        total_revenue = await order_repository.get_statistics(column_expr, condition, session)

        if total_revenue is None:
            OrderException.fail_get_total_revenue()

        return total_revenue

