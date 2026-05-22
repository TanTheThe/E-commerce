from src.crud.order.services.create_order.data_loader import DataLoaderService
from src.crud.order.services.create_order.inventory_order import InventoryService
from src.crud.order.services.create_order.offer_order import OfferService
from src.crud.order.services.create_order.order_calculation import OrderCalculationService
from src.crud.order.repositories import OrderRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.order import OrderException
from src.schemas.order import OrderCreateModel, PaymentStatusOrderType

order_repository = OrderRepository()
order_detail_repository = OrderDetailRepository()
data_loader_service = DataLoaderService()
offer_service = OfferService()
order_calculation_service = OrderCalculationService()
inventory_service = InventoryService()


class CreateOrderService:
    async def create_order(self, customer_id: str, order_data: OrderCreateModel, session: AsyncSession):
        try:
            customer, address = await data_loader_service.validate_customer_and_address(
                customer_id,
                order_data.address_id,
                session
            )

            order_offer = await offer_service.validate_and_get_order_offer(order_data.special_offer_id, session)

            order_items_map = {
                item.product_variant_id: item.quantity
                for item in order_data.order_detail
            }
            variant_ids = set(order_items_map.keys())

            variant_map = await data_loader_service.load_variants_with_relations(
                variant_ids,
                session
            )

            product_offers_to_update = await offer_service.validate_product_offers(
                list(variant_map.values()),
                order_items_map
            )

            color_ids = {
                str(v.color_id) for v in variant_map.values()
                if v.color_id
            }

            color_map = await data_loader_service.load_colors_batch(color_ids, session)

            sub_total, product_discount, order_detail_objs, product_offers_to_update = \
                await order_calculation_service.calculate_order_totals(
                    order_items_map,
                    variant_map,
                    color_map,
                    session
                )

            order_discount = offer_service.calculate_order_discount(
                order_offer,
                sub_total
            )

            discount_percent = offer_service.calculate_discount_percent(
                order_offer,
                order_discount,
                sub_total
            )

            total_discount = product_discount + order_discount
            total_price = sub_total - order_discount

            if total_price < 0:
                OrderException.invalid_price()

            special_offer_snapshot = offer_service.create_offer_snapshot(order_offer)

            address_snapshot = {
                "line": address.line,
                "ward": {
                    "id": str(address.ward.id),
                    "name": address.ward.name,
                    "code_name": address.ward.code_name,
                    "division_type": address.ward.division_type
                },
                "province": {
                    "id": str(address.province.id),
                    "name": address.province.name,
                    "code_name": address.province.code_name,
                    "division_type": address.province.division_type,
                    "phone_code": address.province.phone_code
                },
                "district": address.district,
                "country": address.country
            }

            payment_status = self.determine_payment_status(order_data.payment_method)

            order_code = await order_repository.generate_ord_number(session)
            new_order_dict = {
                "code": order_code,
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
                "address_snapshot": address_snapshot,
                "special_offer_snapshot": special_offer_snapshot
            }

            new_order = await order_repository.create_order(new_order_dict, session)

            for od in order_detail_objs:
                od.order_id = new_order.id

            await order_detail_repository.create_order_detail(order_detail_objs, session)

            if order_data.payment_method in ["direct", "vnpay"]:
                await inventory_service.update_inventory_batch(
                    order_items_map,
                    variant_map,
                    session
                )

            if order_data.payment_method == "direct":
                await offer_service.update_offers_usage(
                    product_offers_to_update,
                    order_offer,
                    customer_id,
                    session
                )

                await inventory_service.update_product_stats(
                    order_items_map,
                    variant_map,
                    session
                )

            await session.commit()

            return {
                "order_id": str(new_order.id),
                "order_code": new_order.code,
                "sub_total": sub_total,
                "total_price": total_price,
                "product_discount": product_discount,
                "order_discount": order_discount,
                "total_discount": total_discount,
                "discount_percent": discount_percent,
                "status": new_order.status,
                "payment_method": new_order.payment_method,
                "payment_status": new_order.payment_status,
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
                    "ward": {
                        "id": str(address.ward.id),
                        "name": address.ward.name,
                        "code_name": address.ward.code_name,
                    },
                    "province": {
                        "id": str(address.province.id),
                        "name": address.province.name,
                        "code_name": address.province.code_name,
                    },
                    "district": address.district,
                    "country": address.country,
                },
                "order_detail": [
                    {
                        "quantity": od.quantity,
                        "price": od.price,
                        "price_before_discount": od.product_snapshot.get("price_before_discount"),
                        "product_id": str(od.product_id),
                        "product_variant_id": str(od.product_variant_id),
                        "product_name": od.product_snapshot.get("name"),
                        "product_image": od.product_snapshot.get("product_image"),
                        "variant_image": od.product_snapshot.get("variant_image"),
                        "size": od.product_snapshot.get("size"),
                        "color": od.product_snapshot.get("color_name"),
                    }
                    for od in order_detail_objs
                ]
            }

        except Exception as e:
            await session.rollback()
            raise


    def determine_payment_status(self, payment_method: str) -> str:
        if payment_method == "direct":
            return PaymentStatusOrderType.SUCCESS
        return PaymentStatusOrderType.PENDING

