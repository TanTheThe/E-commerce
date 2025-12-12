from sqlalchemy.orm import selectinload
from src.crud.order.repositories import OrderRepository
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import ReturnOrder, Payment, PaymentRefund
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.return_order import ReturnOrderException

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()

class GetDetailReturnOrderService:
    async def get_detail_return_order(self, return_order_id: str, session: AsyncSession):
        conditions = [ReturnOrder.id == return_order_id]
        joins = [
            selectinload(ReturnOrder.order),
            selectinload(ReturnOrder.user),
            selectinload(ReturnOrder.return_items)
        ]

        return_order = await return_order_repository.get_return_order(conditions, session, joins)
        if not return_order:
            ReturnOrderException.return_doesnt_exist()

        refund_info = None
        if return_order.order.payment_method == "vnpay":
            payment = await vnpay_repository.get_payment(
                and_(Payment.order_id == return_order.order_id, Payment.status == "success"),
                session
            )
            if payment:
                refund = await payment_refund_repository.get_payment_refund(
                    and_(PaymentRefund.payment_id == payment.id),
                    session
                )
                if refund:
                    refund_info = {
                        "refund_id": str(refund.id),
                        "status": refund.status,
                        "amount": refund.refund_amount,
                        "response_code": refund.response_code,
                        "created_at": str(refund.created_at),
                        "attempt_count": refund.attempt_count,
                    }

        return_order_dict = {
            "id": str(return_order.id),
            "order_id": str(return_order.order_id),
            "user_id": str(return_order.user_id),
            "reason": return_order.reason,
            "status": return_order.status,
            "note": return_order.note,
            "created_at": str(return_order.created_at),
            "approved_at": str(return_order.approved_at),
            "rejected_at": str(return_order.rejected_at),
            "refunded_at": str(return_order.refunded_at),
            "order": {
                "id": str(return_order.order.id),
                "code": return_order.order.code,
                "total_price": return_order.order.total_price,
                "payment_method": return_order.order.payment_method,
                "payment_status": return_order.order.payment_status,
                "delivered_at": str(return_order.order.delivered_at)
            } if return_order.order else None,
            "user": {
                "id": str(return_order.user.id),
                "email": return_order.user.email,
                "first_name": return_order.user.first_name,
                "last_name": return_order.user.last_name
            } if return_order.user else None,
            "return_items": [
                {
                    "id": str(item.id),
                    "order_detail_id": str(item.order_detail_id),
                    "quantity": item.quantity,
                    "refund_amount": item.refund_amount,
                    "images": item.images,
                    "created_at": str(item.created_at)
                }
                for item in return_order.return_items
            ] if return_order.return_items else []
        }

        return {
            "return_order": return_order_dict,
            "refund_info": refund_info
        }




