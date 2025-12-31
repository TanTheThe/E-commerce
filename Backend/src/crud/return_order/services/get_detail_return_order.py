from typing import Optional, Dict, Any

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
from sqlmodel import and_, desc
from src.errors.return_order import ReturnOrderException
import logging

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()

logger = logging.getLogger(__name__)

class GetDetailReturnOrderService:
    async def get_detail_return_order(self, return_order_id: str, session: AsyncSession):
        conditions = [ReturnOrder.id == return_order_id, ReturnOrder.deleted_at.is_(None)]
        options = [
            selectinload(ReturnOrder.order),
            selectinload(ReturnOrder.user),
            selectinload(ReturnOrder.return_items)
        ]

        return_order = await return_order_repository.get_return_order(session=session, where_conditions=conditions,
                                                                      options=options)
        if not return_order:
            ReturnOrderException.return_doesnt_exist()

        refund_info = None
        if return_order.order.payment_method == "vnpay":
            refund_info = await self.get_refund_info(return_order.order_id, session)

        return_order_dict = {
            "id": str(return_order.id),
            "order_id": str(return_order.order_id),
            "user_id": str(return_order.user_id),
            "reason": return_order.reason,
            "status": return_order.status,
            "note": return_order.note,
            "created_at": return_order.created_at.isoformat() if return_order.created_at else None,
            "approved_at": return_order.approved_at.isoformat() if return_order.approved_at else None,
            "rejected_at": return_order.rejected_at.isoformat() if return_order.rejected_at else None,
            "refunded_at": return_order.refunded_at.isoformat() if return_order.refunded_at else None,
            "order": {
                "id": str(return_order.order.id),
                "code": return_order.order.code,
                "total_price": float(return_order.order.total_price),
                "payment_method": return_order.order.payment_method,
                "payment_status": return_order.order.payment_status,
                "delivered_at": return_order.order.delivered_at.isoformat() if return_order.order.delivered_at else None
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
                    "refund_amount": float(item.refund_amount),
                    "images": item.images,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in return_order.return_items
            ] if return_order.return_items else [],
            "total_refund": return_order.total_refund_amount
        }

        return {
            "return_order": return_order_dict,
            "refund_info": refund_info
        }


    async def get_refund_info(self, order_id: str, session: AsyncSession) -> Optional[Dict[str, Any]]:
        try:
            conditions = [
                Payment.order_id == order_id,
                Payment.status == "success"
            ]
            joins = [
                (
                    Payment,
                    {
                        "on": Payment.id == PaymentRefund.payment_id,
                        "type": "inner"
                    }
                )
            ]
            order_by = desc(PaymentRefund.created_at)
            refund = await vnpay_repository.get_payment(session=session, where_conditions=conditions, order_by=order_by,
                                                        joins=joins)

            if refund:
                return {
                    "refund_id": str(refund.id),
                    "status": refund.status,
                    "amount": float(refund.refund_amount),
                    "response_code": refund.response_code,
                    "created_at": refund.created_at.isoformat() if refund.created_at else None,
                    "attempt_count": refund.attempt_count,
                }
        except Exception as e:
            logger.error(f"Error fetching refund info for order {order_id}: {str(e)}")

        return None



