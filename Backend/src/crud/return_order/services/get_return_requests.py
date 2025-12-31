from sqlalchemy.orm import selectinload
from typing import Optional
from sqlmodel import asc, desc
from src.crud.order.repositories import OrderRepository
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import ReturnOrder
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schemas.return_order import ReturnOrderStatus, ReturnOrderSortBy

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()

class GetReturnRequestsService:
    async def get_return_requests(self, session: AsyncSession, status: Optional[ReturnOrderStatus] = None, skip: int = 0,
                                  limit: int = 20, sort_by: ReturnOrderSortBy = ReturnOrderSortBy.CREATED_DESC):
        conditions = [ReturnOrder.deleted_at.is_(None)]

        if status:
            conditions.append(ReturnOrder.status == status.value)

        options = [
            selectinload(ReturnOrder.order),
            selectinload(ReturnOrder.user),
            selectinload(ReturnOrder.return_items)
        ]

        order_clause = self.get_order_clause(sort_by)

        return_orders, total = await return_order_repository.get_all_return_orders(
            where_conditions=conditions,
            session=session,
            skip=skip,
            limit=limit,
            options=options,
            order_by=order_clause,
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
                "total_refund": return_order.total_refund_amount
            }
            returns_dict.append(return_dict)

        return {
            "data": returns_dict,
            "total": total,
        }


    def get_order_clause(self, sort_by: ReturnOrderSortBy):
        sort_mapping = {
            ReturnOrderSortBy.CREATED_ASC: asc(ReturnOrder.created_at),
            ReturnOrderSortBy.CREATED_DESC: desc(ReturnOrder.created_at),
            ReturnOrderSortBy.TOTAL_ASC: asc(ReturnOrder.total_refund),
            ReturnOrderSortBy.TOTAL_DESC: desc(ReturnOrder.total_refund),
        }
        return sort_mapping.get(sort_by, desc(ReturnOrder.created_at))



