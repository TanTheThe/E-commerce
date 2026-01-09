from src.crud.order.repositories import OrderRepository
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import PaymentRefund, Payment, Order
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.payment import PaymentException
from src.schemas.order import PaymentStatusOrderType

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()

class UpdatePaymentRefundStatusService:
    async def update_payment_refund_status(self, refund_id: str, status: str, session: AsyncSession):
        if status not in ["success", "failed"]:
            PaymentException.payment_status_invalid()

        await payment_refund_repository.update_payment_refund(
            and_(PaymentRefund.id == refund_id),
            {"status": status},
            session
        )

        if status == "success":
            refund = await payment_refund_repository.get_payment_refund(
                and_(PaymentRefund.id == refund_id),
                session
            )

            payment = await vnpay_repository.get_payment(
                session=session,
                where_conditions=[Payment.id == refund.payment_id]
            )

            await order_repository.update_order_some_field(
                and_(Order.id == payment.order_id),
                {"payment_status": PaymentStatusOrderType.REFUNDED},
                session
            )

        await session.commit()

        return f"Đã cập nhật trạng thái hoàn tiền thành {status}, vui lòng chuyển khoản thủ công"




