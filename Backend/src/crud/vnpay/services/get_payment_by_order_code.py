from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.order.repositories import OrderRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import Order, Order_Detail, Address, Payment
from src.errors.order import OrderException

order_repository = OrderRepository()
vnpay_repository = VNPayRepository()

class GetPaymentByOrderCodeService:
    async def get_payment_result_by_order_code(self, order_code: str, session: AsyncSession) -> dict:
        condition_order = [Order.code == order_code, Order.deleted_at.is_(None)]
        options = [
            selectinload(Order.order_detail).selectinload(Order_Detail.product_variant),
            selectinload(Order.user),
            selectinload(Order.address).selectinload(Address.ward),
            selectinload(Order.address).selectinload(Address.province)
        ]

        order = await order_repository.get_order(session=session, where_conditions=condition_order, options=options)

        if not order:
            OrderException.not_found()

        condition_payment = [Payment.order_id == order.id]
        payment = await vnpay_repository.get_payment(session=session, where_conditions=condition_payment)

        if not payment:
            OrderException.payment_not_found()

        return self.build_detailed_payment_result(order, payment)

    def build_detailed_payment_result(self, order: Order, payment: Payment) -> dict:
        return {
            "order_id": str(order.id),
            "order_code": order.code,
            "order_status": order.status,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "payment_details": {
                "payment_id": str(payment.id),
                "transaction_no": payment.transaction_no,
                "bank_code": payment.bank_code,
                "bank_tran_no": payment.bank_tran_no,
                "card_type": payment.card_type,
                "response_code": payment.response_code,
                "transaction_status": payment.transaction_status,
                "pay_date": payment.pay_date.isoformat() if payment.pay_date else None,
                "amount": payment.amount,
                "order_info": payment.order_info,
                "status": payment.status
            },
            "order_summary": {
                "sub_total": order.sub_total,
                "discount": order.discount,
                "discount_percent": float(order.discount_percent) if order.discount_percent else 0.0,
                "total_price": order.total_price,
                "note": order.note
            },
            "customer": {
                "id": str(order.user.id),
                "name": f"{order.user.first_name} {order.user.last_name}",
                "email": order.user.email,
                "phone": order.user.phone_number
            } if order.user else None,
            "address": {
                "line": order.address.line,
                "ward": order.address.ward.name if order.address.ward else None,
                "district": order.address.district,
                "province": order.address.province.name if order.address.province else None,
                "country": order.address.country
            } if order.address else None,
            "order_items": [
                {
                    "product_variant_id": str(od.product_variant_id),
                    "product_name": od.product_snapshot.get("name"),
                    "quantity": od.quantity,
                    "price": od.price,
                    "size": od.product_snapshot.get("size"),
                    "color": od.product_snapshot.get("color_name"),
                    "image": od.product_snapshot.get("variant_image") or od.product_snapshot.get("product_image")
                }
                for od in order.order_detail
            ],
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None
        }