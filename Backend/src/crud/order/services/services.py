from datetime import datetime
from sqlalchemy.orm import selectinload, joinedload, noload, load_only
from src.crud.notification.services import NotificationService
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import User, Order, Order_Detail, OrderStatusHistory
from src.crud.address.repositories import AddressRepository
from src.crud.order.repositories import OrderRepository
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.user.repositories import UserRepository
from src.crud.product.repositories import ProductRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.color.repositories import ColorRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, func, or_, asc, desc, update, select
from src.errors.order import OrderException
from src.schemas.order import OrderFilterModel, CancellationStatusType

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

class OrderService:
    async def get_detail_order_admin(self, order_id: str, session: AsyncSession):
        joins = [
            selectinload(Order.order_detail).load_only(
                Order_Detail.id,
                Order_Detail.Product
            ),
            selectinload(Order.user).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.email,
                User.phone,
            ),
        ]

        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        order = await order_repository.get_order(condition, session, joins)

        if not order:
            OrderException.not_found()

        user = order.user
        user_response = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
        } if user else None

        address = order.address_snapshot
        address_response = {
            "line": address.get("line"),
            "street": address.get("street"),
            "ward": address.get("ward"),
            "city": address.get("city"),
            "district": address.get("district"),
            "country": address.get("country"),
        } if address else None

        order_detail_response = []
        for od in order.order_detail:
            product_snapshot = od.Product

            product_dict = {
                "id": str(od.id),
                "name": product_snapshot.get("name"),
                "images": product_snapshot.get("images", []),
                "price": product_snapshot.get("price"),
                "quantity": product_snapshot.get("quantity"),
                "size": product_snapshot.get("size"),
                "color": product_snapshot.get("color"),
            }

            order_detail_response.append(product_dict)

        response = {
            "order": {
                "id": str(order.id),
                "code": order.code,
                "note": order.note,
                "status": order.status,
                "created_at": str(order.created_at),
                "sub_total": order.sub_total,
                "discount": order.discount,
                "total_price": order.total_price,
            },
            "customer": user_response,
            "address": address_response,
            "order_detail": order_detail_response
        }

        return response

    async def get_detail_order_customer(self, order_id: str, customer_id: str, session: AsyncSession):
        joins = [
            selectinload(Order.order_detail), selectinload(Order.user),
        ]

        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        order = await order_repository.get_order(condition, session, joins)

        if not order:
            OrderException.not_found()

        if str(order.user_id) != str(customer_id):
            OrderException.unauthorized_order()

        user = order.user
        user_response = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
        } if user else None

        address = order.address_snapshot
        address_response = {
            "line": address["line"],
            "street": address["street"],
            "ward": address["ward"],
            "city": address["city"],
            "district": address["district"],
            "country": address["country"],
        } if address else None

        condition_status = and_(OrderStatusHistory.order_id == order_id)
        latest_status = await order_repository.get_new_status_order(condition_status, session)
        latest_status_response = None
        if latest_status:
            latest_status_response = {
                "status": latest_status.status,
                "changed_at": str(latest_status.created_at),
            }

        order_detail_response = []
        for od in order.order_detail:
            product_dict = {
                "name": od.Product["name"],
                "size": od.Product["size"],
                "color_name": od.Product["color_name"],
                "product_image": od.Product["product_image"],
                "variant_image": od.Product["variant_image"],
                "price_after_discount": od.Product["price_after_discount"],
                "price_before_discount": od.Product["price_before_discount"],
                "quantity": od.quantity
            }

            order_detail_response.append(product_dict)

        response = {
            "order": {
                "code": order.code,
                "note": order.note,
                "status": order.status,
                "created_at": str(order.created_at),
                "last_status_change": latest_status_response,
                "sub_total": order.sub_total,
                "discount": order.discount,
                "total_price": order.total_price,
            },
            "customer": user_response,
            "address": address_response,
            "order_detail": order_detail_response
        }

        return response

    async def get_all_order_customer(self, user_id: str, status_order: str, session: AsyncSession, skip: int = 0,
                                     limit: int = 10):
        condition = [Order.user_id == user_id, Order.status == status_order, Order.deleted_at.is_(None)]
        if status_order == 'delivered':
            joins = [selectinload(Order.order_detail).selectinload(Order_Detail.evaluate)]
        else:
            joins = [selectinload(Order.order_detail)]

        orders, total = await order_repository.get_all_order(condition, session, skip=skip, limit=limit, joins=joins)

        order_response = []
        for order in orders:
            product_map = {}

            for od in order.order_detail:
                pid = str(od.product_id)
                product = od.Product

                if pid not in product_map:
                    product_map[pid] = {
                        "product_id": pid,
                        "name": product["name"],
                        "variant_image": product["variant_image"],
                        "price_after_discount": product["price_after_discount"],
                        "price_before_discount": product["price_before_discount"],
                        "variants": []
                    }

                variant_info = {
                    "size": product["size"],
                    "color_name": product["color_name"],
                    "quantity": od.quantity,
                    "order_detail_id": str(od.id)
                }

                if status_order == 'delivered':
                    has_evaluation = od.evaluate is not None and od.evaluate.deleted_at is None
                    variant_info["has_evaluation"] = has_evaluation

                    if has_evaluation:
                        variant_info["evaluation_id"] = str(od.evaluate.id)
                        has_additional_evaluation = (
                                od.evaluate.additional_comment is not None or
                                od.evaluate.additional_image is not None
                        )
                        variant_info["has_additional_evaluation"] = has_additional_evaluation

                product_map[pid]["variants"].append(variant_info)

            can_show_cancel_button = self.can_show_cancel_button(order)
            has_pending_cancellation = order.cancellation_status == CancellationStatusType.REQUESTED

            order_response.append({
                "order": {
                    "order_id": str(order.id),
                    "code": order.code,
                    "status": order.status,
                    "created_at": str(order.created_at),
                    "discount": order.discount,
                    "total_price": order.total_price,
                    "can_show_cancel_button": can_show_cancel_button,
                    "has_pending_cancellation": has_pending_cancellation,
                    "cancellation_status": order.cancellation_status,
                    "cancellation_reason": order.cancellation_reason if has_pending_cancellation else None
                },
                "order_detail": list(product_map.values())
            })

        return {"total": total, "data": order_response}

    def can_show_cancel_button(self, order: Order) -> bool:
        if order.status in ["cancelled", "delivered", "shipping"]:
            return False

        if order.cancellation_status == CancellationStatusType.REQUESTED:
            return False

        if order.status in ["pending", "confirmed"]:
            return True

        return False

    async def get_all_order_admin(self, session: AsyncSession, filter_data: OrderFilterModel, skip: int = 0,
                                  limit: int = 10):
        conditions = [Order.deleted_at.is_(None), User.deleted_at.is_(None)]

        if filter_data.search:
            search_term = f"%{filter_data.search}%"
            full_name_search = func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
            conditions.append(or_(
                Order.code.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                full_name_search
            ))
            need_user_join = True
        else:
            need_user_join = False

        if filter_data.status:
            conditions.append(Order.status == filter_data.status)

        order_by = []
        if filter_data.sort_by_total_price:
            if filter_data.sort_by_total_price == "cheapest":
                order_by.append(asc(Order.total_price))
            else:
                order_by.append(desc(Order.total_price))

        if filter_data.sort_by_created_at:
            if filter_data.sort_by_created_at == "newest":
                order_by.append(desc(Order.created_at))
            else:
                order_by.append(asc(Order.created_at))

        joins = [
            joinedload(Order.user).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.deleted_at,
            ),
        ]
        orders, total = await order_repository.get_all_order(conditions, session, order_by, skip=skip, limit=limit,
                                                             joins=joins, join_user=need_user_join)

        response = []
        for order in orders:
            user = order.user
            customer_name = f"{user.first_name} {user.last_name}" if user else None

            order_dict = {
                "id": str(order.id),
                "code": order.code,
                "status": order.status,
                "created_at": str(order.created_at),
                "total_price": order.total_price,
                "sub_total": order.sub_total,
                "discount": order.discount,
                "customer_name": customer_name,
                "payment_method": order.payment_method,
            }
            response.append(order_dict)

        return {
            "data": response,
            "total": total,
        }

    async def update_status(self, order_id, status, session: AsyncSession):
        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        joins = [
            selectinload(Order.order_detail).load_only(Order_Detail.product_id),
        ]
        order_to_update = await order_repository.get_order(condition, session, joins)

        if order_to_update is None:
            OrderException.not_found()

        if order_to_update.cancellation_status == CancellationStatusType.REQUESTED:
            OrderException.cant_update_cancel_order()

        if order_to_update.cancellation_status == CancellationStatusType.APPROVED:
            OrderException.cant_reverse_cancel_order()

        status_dict = status.model_dump()

        if status_dict.get("status") == "delivered":
            status_dict["delivered_at"] = datetime.now()
            
        order_after_update = await order_repository.update_order(order_to_update, status_dict, session)

        history_entry = OrderStatusHistory(
            order_id=order_id,
            status=order_after_update.status,
            created_at=datetime.now()
        )
        session.add(history_entry)

        await session.commit()
        return order_after_update
    

    async def confirm_order_received(self, order_id: str, session: AsyncSession):
        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        joins = [
            selectinload(Order.order_detail).load_only(Order_Detail.product_id),
        ]
        
        order_to_update = await order_repository.get_order(condition, session, joins)
        if order_to_update is None:
            OrderException.not_found()
        
        if order_to_update.cancellation_status == CancellationStatusType.REQUESTED:
            OrderException.cant_update_cancel_order()
        if order_to_update.cancellation_status == CancellationStatusType.APPROVED:
            OrderException.cant_reverse_cancel_order()
        
        if order_to_update.status != "delivered":
            raise OrderException.invalid_status_transition(
                f"Không thể xác nhận nhận hàng. Đơn hàng phải ở trạng thái 'Đã giao hàng', hiện tại là '{order_to_update.status}'"
            )
        
        if order_to_update.status == "received":
            raise OrderException.already_received(
                "Đơn hàng đã được xác nhận nhận hàng trước đó"
            )
        
        update_data = {
            "status": "received",
            "received_at": datetime.now()
        }
        
        order_after_update = await order_repository.update_order(order_to_update, update_data, session)
        
        history_entry = OrderStatusHistory(
            order_id=order_id,
            status=order_after_update.status,
            created_at=datetime.now(),
        )
        session.add(history_entry)
        await session.commit()
        
        return order_after_update

    async def count_new_orders(self, to_date, from_date, session: AsyncSession):
        condition = and_(Order.created_at >= from_date, Order.created_at <= to_date)
        orders = await order_repository.count_orders(condition, session)

        if orders is None:
            OrderException.not_found()

        return len(orders)

    async def get_total_sales(self, today, seven_days_ago, session: AsyncSession):
        condition = and_(Order.created_at >= seven_days_ago, Order.status == "delivered")
        column_expr = func.coalesce(func.sum(Order.sub_total), 0)
        total_sales = await order_repository.get_statistics(column_expr, condition, session)

        if total_sales is None:
            OrderException.fail_get_total_sales()

        return total_sales

    async def get_total_revenue(self, today, seven_days_ago, session: AsyncSession):
        condition = and_(Order.created_at >= seven_days_ago, Order.status == "delivered")
        column_expr = func.coalesce(func.sum(Order.total_price), 0)
        total_revenue = await order_repository.get_statistics(column_expr, condition, session)

        if total_revenue is None:
            OrderException.fail_get_total_revenue()

        return total_revenue

