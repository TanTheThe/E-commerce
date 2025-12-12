from typing import Dict
from src.database.models import Order_Detail
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.product import ProductException


class OrderCalculationService:
    async def calculate_order_totals(self, order_items_map: Dict[str, int],     # {variant_id: quantity}
                                     variant_map, color_map,
                                     session: AsyncSession):

        sub_total = 0                       # Tổng tiền sau product discount
        total_product_discount = 0          # Tổng discount từ product offers
        order_detail_objs = []              # List các Order_Detail objects
        product_offers_to_update = {}       # Dict {offer_id: quantity}

        for variant_id, quantity in order_items_map.items():
            variant = variant_map.get(variant_id)
            if not variant:
                ProductException.not_found_variant()

            product = variant.product
            if not product:
                ProductException.not_found()

            if quantity > variant.quantity:
                ProductException.out_of_stock(str(variant.id))

            discounted_price = variant.price
            product_discount_per_item = 0

            if product.special_offer_id and product.special_offer:
                product_offer = product.special_offer

                if product_offer.scope == "product":

                    if product_offer.type == "percent":
                        product_discount_per_item = (variant.price * product_offer.discount) / 100
                        discounted_price = variant.price - product_discount_per_item
                        discounted_price = int(round(discounted_price / 1000) * 1000)

                        if str(product_offer.id) not in product_offers_to_update:
                            product_offers_to_update[str(product_offer.id)] = 0
                        product_offers_to_update[str(product_offer.id)] += quantity

                    elif product_offer.type == "fixed":
                        product_discount_per_item = min(product_offer.discount, variant.price)
                        discounted_price = variant.price - product_discount_per_item

                        if str(product_offer.id) not in product_offers_to_update:
                            product_offers_to_update[str(product_offer.id)] = 0
                        product_offers_to_update[str(product_offer.id)] += quantity

            item_sub_total = discounted_price * quantity
            item_total_discount = product_discount_per_item * quantity

            sub_total += item_sub_total
            total_product_discount += item_total_discount

            color = color_map.get(str(variant.color_id)) if variant.color_id else None

            product_snapshot = {
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
                "quantity": quantity,
                "price": discounted_price,
                "product_id": variant.product_id,
                "product_variant_id": variant.id,
                "product_snapshot": product_snapshot
            }

            order_detail_objs.append(Order_Detail(**order_detail_dict))

        return sub_total, total_product_discount, order_detail_objs, product_offers_to_update