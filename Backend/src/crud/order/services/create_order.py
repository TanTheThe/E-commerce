from datetime import datetime
from sqlalchemy.orm import selectinload
from src.crud.notification.services import NotificationService
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import Special_Offer, User, Address, Order_Detail, Product_Variant, Product, Color
from src.crud.address.repositories import AddressRepository
from src.crud.order.repositories import OrderRepository
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.user.repositories import UserRepository
from src.crud.product.repositories import ProductRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.color.repositories import ColorRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from sqlalchemy import update
from src.errors.address import AddressException
from src.errors.product import ProductException
from src.errors.special_offer import SpecialOfferException
from src.schemas.order import OrderCreateModel, PaymentStatusOrderType
import time
import uuid
from src.errors.authentication import AuthException

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

class CreateOrderService:
    async def validate_order_dependencies(self, customer_id, address_id, offer_id, session):
        conditions_user = and_(User.id == customer_id, User.deleted_at.is_(None))
        customer = await user_repository.get_user(conditions_user, session)
        if not customer:
            AuthException.user_not_found()

        conditions_address = and_(Address.id == address_id, Address.deleted_at.is_(None))
        address = await address_repository.get_address(conditions_address, session)
        if not address:
            AddressException.not_found()

        order_offer = None
        if offer_id:
            conditions_offer = [
                Special_Offer.id == offer_id,
                Special_Offer.deleted_at.is_(None),
                Special_Offer.scope == "order"
            ]
            order_offer = await special_offer_repository.get_special_offer(session=session, where_conditions=conditions_offer)
            if not order_offer:
                SpecialOfferException.not_found()

        return customer, address, order_offer

    async def get_variants_with_product_offers(self, variant_ids, session):
        condition = [Product_Variant.id.in_(variant_ids)]
        options = [
            selectinload(Product_Variant.product).options(
                selectinload(Product.special_offer),
            ).load_only(
                Product.id,
                Product.name,
                Product.images,
                Product.special_offer_id
            ),
        ]

        variants, _ = await product_variant_repository.get_all_product_variant(session=session, where_conditions=condition, options=options, for_update=True)
        return {str(v.id): v for v in variants}

    async def calculate_order_totals(self, order_items, variant_map, session: AsyncSession):
        try:
            sub_total = 0
            total_discount = 0
            order_detail_objs = []
            product_offers_to_update = {}

            for item in order_items:
                variant = variant_map.get(str(item.product_variant_id))
                if not variant:
                    ProductException.not_found_variant()

                product = variant.product
                if not product:
                    ProductException.not_found()

                if item.quantity > variant.quantity:
                    ProductException.out_of_stock(str(variant.id))

                discounted_price = variant.price
                product_discount_per_item = 0
                if product.special_offer_id and product.special_offer:
                    product_offer = product.special_offer
                    if product_offer.scope == "product":
                        remaining_quantity = product_offer.total_quantity - product_offer.used_quantity
                        if remaining_quantity < item.quantity:
                            raise Exception(f"Product offer {product_offer.code} không đủ số lượng")

                        if product_offer.type == "percent":
                            product_discount_per_item = (variant.price * product_offer.discount) / 100
                            discounted_price = variant.price - product_discount_per_item
                            discounted_price = int(round(discounted_price / 1000) * 1000)

                            if str(product_offer.id) not in product_offers_to_update:
                                product_offers_to_update[str(product_offer.id)] = 0
                            product_offers_to_update[str(product_offer.id)] += item.quantity

                item_sub_total = discounted_price * item.quantity
                item_total_discount = product_discount_per_item * item.quantity

                sub_total += item_sub_total
                total_discount += item_total_discount

                color = None
                if variant.color_id:
                    condition = and_(Color.id == variant.color_id, Color.deleted_at.is_(None))
                    color = await color_repository.get_color(condition, session)

                product_dict = {
                    "name": product.name,
                    "product_image": product.images,
                    "price_before_discount": variant.price,
                    "price_after_discount": discounted_price,
                    "variant_image": variant.image,
                    "size": variant.size,
                    "color_id": str(variant.color_id) if variant.color_id else None,
                    "color_name": color.name if color else variant.color_name,
                    "color_code": color.code if color else variant.color_code,
                }

                order_detail_dict = {
                    "quantity": item.quantity,
                    "price": discounted_price,
                    "product_id": variant.product_id,
                    "product_variant_id": variant.id,
                    "product_snapshot": product_dict
                }

                order_detail_objs.append(Order_Detail(**order_detail_dict))

            return sub_total, total_discount, order_detail_objs, product_offers_to_update

        except Exception as e:
            raise

    async def apply_order_offer(self, order_offer, sub_total):
        try:
            if not order_offer:
                return 0

            if order_offer.condition and sub_total < order_offer.condition:
                return 0

            remaining_quantity = order_offer.total_quantity - order_offer.used_quantity
            if remaining_quantity < 1:
                raise Exception(f"Order offer {order_offer.code} đã hết lượt sử dụng")

            order_discount = 0
            if order_offer.type == "percent":
                order_discount = int(sub_total * order_offer.discount / 100)
            elif order_offer.type == "fixed":
                order_discount = order_offer.discount

            return order_discount
        except Exception as e:
            raise

    def calculate_discount_percent(self, order_offer, order_discount, sub_total):
        if not order_offer or order_discount == 0:
            return 0
        
        if order_offer.type == "percent":
            return order_offer.discount
        elif order_offer.type == "fixed":
            if sub_total > 0:
                return round((order_discount / sub_total) * 100, 2)
            return 0
        
        return 0
    
    def create_special_offer_snapshot(self, order_offer):
        if not order_offer:
            return None
            
        return {
            "id": str(order_offer.id),
            "code": order_offer.code,
            "name": order_offer.name,
            "discount": order_offer.discount,
            "condition": order_offer.condition,
            "type": order_offer.type,
            "total_quantity": order_offer.total_quantity,
            "scope": order_offer.scope,
            "used_quantity": order_offer.used_quantity,
            "start_time": order_offer.start_time.isoformat() if order_offer.start_time else None,
            "end_time": order_offer.end_time.isoformat() if order_offer.end_time else None,
            "created_at": order_offer.created_at.isoformat() if order_offer.created_at else None,
            "updated_at": order_offer.updated_at.isoformat() if order_offer.updated_at else None
        }

    async def update_offers_usage(self, product_offers_to_update, order_offer, customer_id, session):
        try:
            if product_offers_to_update:
                offer_ids = list(product_offers_to_update.keys())
                condition = [Special_Offer.id.in_(offer_ids), Special_Offer.deleted_at.is_(None)]
                locked_offers, _ = await special_offer_repository.get_all_special_offer(session=session, where_conditions=condition)

                updates = []
                for offer in locked_offers:
                    quantity_used = product_offers_to_update.get(str(offer.id), 0)
                    if quantity_used > 0:
                        remaining = offer.total_quantity - offer.used_quantity
                        if remaining < quantity_used:
                            SpecialOfferException.insufficient_quantity()

                        updates.append({
                            "id": str(offer.id),
                            "used_quantity": offer.used_quantity + quantity_used
                        })

                if updates:
                    statement = update(Special_Offer)
                    await session.execute(statement, updates)

            if order_offer:
                locked_order_offer = await special_offer_repository.get_special_offer(
                    session=session,
                    where_conditions=[Special_Offer.id == order_offer.id, Special_Offer.deleted_at.is_(None)],
                    for_update=True
                )
                if locked_order_offer:
                    remaining = locked_order_offer.total_quantity - locked_order_offer.used_quantity
                    if remaining < 1:
                        SpecialOfferException.insufficient_quantity()

                    condition = and_(Special_Offer.id == locked_order_offer.id)
                    await special_offer_repository.update_offer_some_field(
                        condition,
                        {
                            "used_quantity": locked_order_offer.used_quantity + 1,
                        },
                        session
                    )

                    user_offer_dict = {
                        "user_id": customer_id,
                        "special_offer_id": order_offer.id,
                        "used_at": datetime.now()
                    }

                    await special_offer_repository.create_user_special_offer(user_offer_dict, session)

        except Exception as e:
            raise

    async def update_inventory_batch(self, order_items, variant_map, session: AsyncSession):
        updates = []
        for item in order_items:
            variant = variant_map[str(item.product_variant_id)]
            if variant.quantity < item.quantity:
                ProductException.out_of_stock(str(variant.id))

            updates.append({
                "id": str(variant.id),
                "quantity": variant.quantity - item.quantity
            })

        if updates:
            statement = update(Product_Variant)
            await session.execute(statement, updates)

    async def update_product_stats(self, order_items, variant_map, session):
        product_updates = {}
        for item in order_items:
            variant = variant_map[str(item.product_variant_id)]
            product_id = str(variant.product_id)
            if product_id not in product_updates:
                product_updates[product_id] = {"total_sold": 0, "popularity_score": 0}

            product_updates[product_id]["total_sold"] += item.quantity
            product_updates[product_id]["popularity_score"] += 1

        for product_id, updates in product_updates.items():
            condition = and_(Product.id == uuid.UUID(product_id))
            await product_repository.update_product_some_field(
                condition,
                {
                    "total_sold": Product.total_sold + updates["total_sold"],
                    "popularity_score": Product.popularity_score + updates["popularity_score"]
                },
                session
            )

    async def create_order(self, customer_id: str, order_data: OrderCreateModel, session: AsyncSession):
        try:
            customer, address, order_offer = await self.validate_order_dependencies(
                customer_id, order_data.address_id, order_data.special_offer_id, session
            )

            variant_ids = {item.product_variant_id for item in order_data.order_detail}
            variant_map = await self.get_variants_with_product_offers(variant_ids, session)

            sub_total, product_discount, order_detail_objs, product_offers_to_update = await self.calculate_order_totals(
                order_data.order_detail, variant_map, session
            )

            order_discount = await self.apply_order_offer(order_offer, sub_total)

            discount_percent = self.calculate_discount_percent(order_offer, order_discount, sub_total)
            special_offer_snapshot = self.create_special_offer_snapshot(order_offer)

            total_discount = product_discount + order_discount
            total_price = sub_total - order_discount

            payment_status = PaymentStatusOrderType.PENDING

            address_dict = {
                "line": address.line,
                "street": address.street,
                "ward": address.ward,
                "city": address.city,
                "district": address.district,
                "country": address.country
            }

            new_order_dict = {
                "code": str(int(time.time() * 1000)),
                "sub_total": sub_total,
                "total_price": total_price,
                "discount": order_discount,
                "discount_percent": discount_percent,
                "status": "pending",
                "note": order_data.note,
                "payment_method": order_data.payment_method,
                "payment_status": payment_status,
                "user_id": customer_id,
                "special_offer_id": order_data.special_offer_id,
                "address_snapshot": address_dict,
                "special_offer_snapshot": special_offer_snapshot
            }

            new_order = await order_repository.create_order(new_order_dict, session)

            for od in order_detail_objs:
                od.order_id = new_order.id
            await order_detail_repository.create_order_detail(order_detail_objs, session)

            if order_data.payment_method == "direct":
                await self.update_inventory_batch(order_data.order_detail, variant_map,
                                                  session)
                await self.update_offers_usage(
                    product_offers_to_update, order_offer, customer_id, session
                )
                await self.update_product_stats(order_data.order_detail, variant_map, session)

            await session.commit()

            response = {
                "order_id": str(new_order.id),
                "order_code": new_order.code,
                "sub_total": sub_total,
                "total_price": total_price,
                "product_discount": product_discount,
                "order_discount": order_discount,
                "total_discount": total_discount,
                "discount_percent": discount_percent,
                "note": new_order.note,
                "order_offer": {
                    "id": str(order_offer.id),
                    "code": order_offer.code,
                    "name": order_offer.name,
                    "discount": order_offer.discount,
                    "condition": order_offer.condition,
                    "type": order_offer.type,
                } if order_offer else None,
                "address": {
                    "id": str(address.id),
                    "line": address.line,
                    "street": address.street,
                    "ward": address.ward,
                    "city": address.city,
                    "district": address.district,
                    "country": address.country,
                },
                "order_detail": [
                    {
                        "quantity": od.quantity,
                        "price": str(od.price),  # Giá sau discount
                        "product_id": str(od.product_id),
                        "product_variant_id": str(od.product_variant_id)
                    }
                    for od in order_detail_objs
                ]
            }

            return response
        except Exception as e:
            await session.rollback()
            raise

