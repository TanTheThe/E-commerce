from sqlalchemy.orm import selectinload
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
from sqlmodel import desc

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
notification_service = NotificationService()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()

class GetCustomerReturnsService:
    async def get_customer_returns(self, user_id: str, session: AsyncSession, skip: int = 0, limit: int = 20):
        conditions = [
            ReturnOrder.user_id == user_id,
            ReturnOrder.deleted_at.is_(None)
        ]
        joins = [
            selectinload(ReturnOrder.order),
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
                "reason": return_order.reason,
                "status": return_order.status,
                "note": return_order.note,
                "created_at": return_order.created_at,
                "approved_at": return_order.approved_at,
                "rejected_at": return_order.rejected_at,
                "refunded_at": return_order.refunded_at,
                "order": {
                    "id": str(return_order.order.id),
                    "code": return_order.order.code,
                    "total_price": return_order.order.total_price,
                    "payment_method": return_order.order.payment_method,
                    "payment_status": return_order.order.payment_status,
                    "delivered_at": return_order.order.delivered_at
                } if return_order.order else None,
                "return_items": [
                    {
                        "id": str(item.id),
                        "order_detail_id": str(item.order_detail_id),
                        "quantity": item.quantity,
                        "refund_amount": item.refund_amount,
                        "images": item.images
                    }
                    for item in return_order.return_items
                ] if return_order.return_items else [],
                "total_refund": sum(
                    item.refund_amount for item in return_order.return_items) if return_order.return_items else 0
            }
            returns_dict.append(return_dict)

        return returns_dict, total