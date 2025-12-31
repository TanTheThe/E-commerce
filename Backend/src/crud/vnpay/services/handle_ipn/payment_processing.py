from datetime import datetime

from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.cash.repositories import CashRepository
from src.crud.order.repositories import OrderRepository
from src.crud.order.services.create_order.data_loader import DataLoaderService
from src.crud.order.services.create_order.inventory_order import InventoryService
from src.crud.order.services.create_order.offer_order import OfferService
from src.crud.vnpay.repositories import VNPayRepository
from src.crud.vnpay.services.handle_ipn.payment_data import PaymentDataService
from src.crud.vnpay.services.handle_ipn.revenue_tracking import RevenueTrackingService
from src.crud.vnpay.services.handle_ipn.vnpay_validation import VNPayValidationService
from src.database.models import Order, Payment
from src.errors.order import OrderException
import logging

from src.schemas.order import PaymentStatusOrderType

logger = logging.getLogger(__name__)

data_loader_service = DataLoaderService()
offer_service = OfferService()
inventory_service = InventoryService()
payment_data_service = PaymentDataService()
revenue_tracking_service = RevenueTrackingService()
validation_service = VNPayValidationService()
cash_repository = CashRepository()

order_repository = OrderRepository()
vnpay_repository = VNPayRepository()


class PaymentProcessingService:
    async def process_successful_payment(self, order: Order, session: AsyncSession) -> None:
        order_items_map = {
            str(od.product_variant_id): od.quantity
            for od in order.order_detail
        }

        variant_ids = set(order_items_map.keys())

        variant_map = await data_loader_service.load_variants_with_relations(variant_ids, session)

        color_ids = {
            str(v.color_id) for v in variant_map.values()
            if v.color_id
        }

        color_map = await data_loader_service.load_colors_batch(color_ids, session)

        order_offer = None
        if order.special_offer_id:
            order_offer = await offer_service.validate_and_get_order_offer(
                str(order.special_offer_id),
                session
            )

        product_offers_to_update = await offer_service.validate_product_offers(
            list(variant_map.values()),
            order_items_map
        )

        await inventory_service.update_inventory_batch(
            order_items_map, variant_map, session
        )

        await offer_service.update_offers_usage(
            product_offers_to_update,
            order_offer,
            str(order.order_id),
            session
        )

        await inventory_service.update_product_stats(
            order_items_map,
            variant_map,
            session
        )


    async def process_payment(self, input_data: dict, session: AsyncSession):
        vnpay_data = payment_data_service.extract_vnpay_data(input_data)

        order = await self.load_order_with_details(
            vnpay_data["order_code"],
            session
        )

        if not validation_service.validate_amount(order.total_price, vnpay_data["amount"]):
            OrderException.order_amount_mismatch()

        conditions = [Payment.order_id == order.id]
        existing_payment = await vnpay_repository.get_payment(session=session, where_conditions=conditions)

        if existing_payment:
            logger.info(f"Payment already processed for order {order.code}")
            return payment_data_service.build_payment_response(
                existing_payment,
                vnpay_data["order_code"],
                already_processed=True
            )

        is_success = vnpay_data["response_code"] == "00"
        payment_status = (
            PaymentStatusOrderType.SUCCESS if is_success
            else PaymentStatusOrderType.FAILED
        )

        order.payment_status = payment_status
        session.add(order)

        if is_success:
            await self.process_successful_payment(
                order,
                session
            )

        payment = await self.create_payment_record(
            order,
            vnpay_data,
            payment_status,
            session
        )

        cash_transaction = None
        if is_success:
            cash_transaction = await revenue_tracking_service.create_revenue_transaction(
                order,
                payment,
                vnpay_data["pay_date"],
                session
            )

        await session.commit()

        return payment_data_service.build_payment_response(
            payment,
            vnpay_data["order_code"],
            cash_transaction,
            already_processed=False
        )

    async def load_order_with_details(self, order_code: str, session: AsyncSession) -> Order:
        condition = [Order.code == order_code, Order.deleted_at.is_(None)]
        options = [selectinload(Order.order_detail), selectinload(Order.user)]

        order = await order_repository.get_order(session=session, where_conditions=condition, options=options)

        if not order:
            OrderException.not_found()

        return order

    async def create_payment_record(self, order: Order, vnpay_data: dict, payment_status: str, session: AsyncSession) -> Payment:
        payment_dict = {
            "order_id": order.id,
            "payment_gateway": "vnpay",
            "txn_ref": vnpay_data["txn_ref"],
            "transaction_no": vnpay_data["transaction_no"],
            "bank_tran_no": vnpay_data["bank_tran_no"],
            "bank_code": vnpay_data["bank_code"],
            "card_type": vnpay_data["card_type"],
            "transaction_status": vnpay_data["transaction_status"],
            "tmn_code": vnpay_data["tmn_code"],
            "pay_date": vnpay_data["pay_date"],
            "amount": vnpay_data["amount"],
            "response_code": vnpay_data["response_code"],
            "order_info": vnpay_data["order_desc"],
            "status": payment_status
        }

        return await vnpay_repository.create_payment(payment_dict, session)





