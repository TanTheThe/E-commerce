from sqlalchemy.orm import selectinload
from typing import Optional
from src.crud.notification.services.services import NotificationService
from src.crud.order.repositories import OrderRepository
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import ReturnOrder
from sqlmodel.ext.asyncio.session import AsyncSession

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
notification_service = NotificationService()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()

class GetReturnRequestsService:
    async def get_return_requests(self, session: AsyncSession, status: Optional[str] = None, skip: int = 0,
                                  limit: int = 20):
        conditions = []
        if status:
            conditions.append(ReturnOrder.status == status)

        joins = [
            selectinload(ReturnOrder.order),
            selectinload(ReturnOrder.user),
            selectinload(ReturnOrder.return_items)
        ]

        return_orders, total = await return_order_repository.get_all_return_orders(
            conditions, session, skip=skip, limit=limit, joins=joins
        )

        returns_dict = []
        for return_order in return_orders:
            return_dict = {
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
                    "payment_status": return_order.order.payment_status
                } if return_order.order else None,
                "user": {
                    "id": str(return_order.user.id),
                    "email": return_order.user.email,
                    "first_name": return_order.user.first_name,
                    "last_name": return_order.user.last_name,
                } if return_order.user else None,
                "return_items_count": len(return_order.return_items) if return_order.return_items else 0,
                "total_refund": sum(
                    item.refund_amount for item in return_order.return_items) if return_order.return_items else 0
            }
            returns_dict.append(return_dict)

        return returns_dict, total



