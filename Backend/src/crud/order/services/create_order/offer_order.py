from datetime import datetime
from typing import Optional, List, Dict
from src.database.models import Special_Offer
from src.crud.special_offer.repositories import SpecialOfferRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from sqlalchemy import update
from src.errors.special_offer import SpecialOfferException


special_offer_repository = SpecialOfferRepository()


class OfferService:
    async def validate_and_get_order_offer(self, offer_id: Optional[str], session):
        if not offer_id:
            return None

        conditions_offer = [
            Special_Offer.id == offer_id,
            Special_Offer.deleted_at.is_(None),
            Special_Offer.scope == "order"
        ]
        order_offer = await special_offer_repository.get_special_offer(
            session=session,
            where_conditions=conditions_offer
        )
        if not order_offer:
            SpecialOfferException.not_found()

        now = datetime.now()
        if order_offer.start_time and now < order_offer.start_time:
            SpecialOfferException.offer_has_not_started(order_offer.code)

        if order_offer.end_time and now > order_offer.end_time:
            SpecialOfferException.offer_has_expired(order_offer.code)

        return order_offer


    async def validate_product_offers(self, variants: List, order_items_map: Dict[str, int]):
        product_offers_to_update = {}

        for variant in variants:
            if not variant.product or not variant.product.special_offer:
                continue

            product_offer = variant.product.special_offer

            if product_offer.scope != "product":
                continue

            now = datetime.now()
            if product_offer.start_time and now < product_offer.start_time:
                continue
            if product_offer.end_time and now > product_offer.end_time:
                continue

            quantity_needed = order_items_map.get(str(variant.id), 0)
            if quantity_needed == 0:
                continue

            remaining_quantity = product_offer.total_quantity - product_offer.used_quantity
            if remaining_quantity < quantity_needed:
                SpecialOfferException.offer_remaining_is_insufficient(product_offer.code, remaining_quantity, quantity_needed)

            if str(product_offer.id) not in product_offers_to_update:
                product_offers_to_update[str(product_offer.id)] = 0

            product_offers_to_update[str(product_offer.id)] += quantity_needed

        return product_offers_to_update


    def calculate_order_discount(self, order_offer, sub_total: int):
        if not order_offer:
            return 0

        if order_offer.condition and sub_total < order_offer.condition:
            return 0

        remaining_quantity = order_offer.total_quantity - order_offer.used_quantity
        if remaining_quantity < 1:
            SpecialOfferException.offer_has_expired(order_offer.code)

        if order_offer.type == "percent":
            discount = int(sub_total * order_offer.discount / 100)
            return discount
        elif order_offer.type == "fixed":
            return min(order_offer.discount, sub_total)

        return 0


    def calculate_discount_percent(self, order_offer, order_discount: int, sub_total: int):
        if not order_offer or order_discount == 0 or sub_total == 0:
            return 0.0

        if order_offer.type == "percent":
            return float(order_offer.discount)
        elif order_offer.type == "fixed":
            return round((order_discount / sub_total) * 100, 2)

        return 0.0


    def create_offer_snapshot(self, order_offer):
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


    async def update_offers_usage(self, product_offers_to_update: Dict[str, int], order_offer,
                                  customer_id: str, session: AsyncSession):
        if product_offers_to_update:
            offer_ids = list(product_offers_to_update.keys())
            condition = [
                Special_Offer.id.in_(offer_ids),
                Special_Offer.deleted_at.is_(None)
            ]

            locked_offers, _ = await special_offer_repository.get_all_special_offer(session=session,
                                                                                    where_conditions=condition,
                                                                                    for_update=True)

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
