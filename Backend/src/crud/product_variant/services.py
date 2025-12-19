from datetime import datetime
import uuid
from typing import List, Set, Dict
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import case
from src.crud.color.repositories import ColorRepository
from src.crud.order.repositories import OrderRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product_Variant, Color, Order_Detail, Order
from src.errors.color import ColorException
from src.errors.product import ProductException
import logging


logger = logging.getLogger(__name__)

product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
order_repository = OrderRepository()


class ProductVariantService:
    async def update_product_variant(self, product_id: str, new_variants: list, session: AsyncSession):
        try:
            if not new_variants:
                ProductException.variants_required()

            if len(new_variants) > 50:
                ProductException.too_many_variants()

            condition = [
                Product_Variant.product_id == product_id,
                Product_Variant.deleted_at.is_(None)
            ]
            existing_variants, _ = await product_variant_repository.get_all_product_variant(session=session, where_conditions=condition)

            existing_dict = {str(v.id): v for v in existing_variants}
            new_dict = {str(v["id"]): v for v in new_variants if v.get("id")}

            invalid_ids = set(new_dict.keys()) - set(existing_dict.keys())
            if invalid_ids:
                raise ProductException.variant_not_belong_to_product(list(invalid_ids))

            await self.validate_skus(new_variants, product_id, session)

            self.validate_variant_combinations(new_variants)

            await self.validate_colors(new_variants, session)

            old_ids = set(existing_dict.keys())
            new_ids = set(new_dict.keys())

            to_soft_delete_ids = old_ids - new_ids

            to_update_ids = new_ids & old_ids

            to_create = [v for v in new_variants if not v.get("id") or str(v.get("id")) not in old_ids]

            if to_soft_delete_ids:
                conditions = [
                    Order_Detail.product_variant_id.in_(to_soft_delete_ids),
                    Order.status.in_(['pending', 'processing', 'confirmed']),
                    Order_Detail.order_id == Order.id
                ]

                order_details = await order_repository.get_all_order(session=session, where_conditions=conditions)

                if order_details:
                    ProductException.cant_delete_variants_in_pending_orders()

            if to_soft_delete_ids:
                for variant_id in to_soft_delete_ids:
                    variant = existing_dict[variant_id]
                    if variant.deleted_at is None:
                        variant.deleted_at = datetime.now()
                        variant.updated_at = datetime.now()

            if to_update_ids:
                to_update_data = await self.prepare_update_data(to_update_ids, new_dict, product_id)
                if to_update_data:
                    await self.bulk_update_variants(to_update_data, session)

            if to_create:
                await self.bulk_create_variants(to_create, product_id, session)

        except Exception as e:
            logger.error(f"Error updating variants for product {product_id}: {str(e)}")
            raise ProductException.variant_update_failed()


    async def bulk_update_variants(self, update_data: Dict[str, dict], session: AsyncSession):
        if not update_data:
            return

        ids = list(update_data.keys())

        def build_case(field: str):
            col = getattr(Product_Variant, field)
            cases = []

            for uid, data in update_data.items():
                field_value = data.get(field)
                cases.append((Product_Variant.id == uid, field_value))

            return case(*cases, else_=col)

        condition = Product_Variant.id.in_(ids)
        values_dict = {
            "size": build_case("size"),
            "image": build_case("image"),
            "color_id": build_case("color_id"),
            "color_name": build_case("color_name"),
            "color_code": build_case("color_code"),
            "price": build_case("price"),
            "quantity": build_case("quantity"),
            "sku": build_case("sku"),
            "deleted_at": build_case("deleted_at"),
            "updated_at": build_case("updated_at"),
        }

        await product_variant_repository.update_product_variant(values_dict, condition, session)


    async def bulk_create_variants(self, items: list[dict], product_id: str, session: AsyncSession):
        await product_variant_repository.create_product_variant(items, product_id, session)


    async def validate_skus(self, variants: List[dict], product_id: str, session: AsyncSession):
        skus = []
        for variant in variants:
            sku = variant.get("sku")
            if sku:
                sku = sku.strip().upper()

                if sku in skus:
                    raise ProductException.duplicate_sku()
                skus.append(sku)

                variant_id = variant.get("id")
                conditions = [
                    Product_Variant.sku == sku,
                    Product_Variant.deleted_at.is_(None),
                ]
                if variant_id:
                    conditions.append(Product_Variant.id != variant_id)
                else:
                    conditions.append(Product_Variant.product_id != product_id)

                exists = await product_variant_repository.get_product_variant(
                    session=session,
                    select_columns=[Product_Variant.id],
                    where_conditions=conditions,
                )
                if exists:
                    ProductException.sku_already_exists()


    def validate_variant_combinations(self, variants: List[dict]):
        combinations = set()

        color_key = ""
        for idx, variant in enumerate(variants):
            size = str(variant.get("size", "")).strip().upper()

            if variant.get("color_id"):
                color_key = str(variant["color_id"])
            elif variant.get("color_name") and variant.get("color_code"):
                color_key = f"{variant['color_name']}_{variant['color_code']}"
            else:
                ProductException.invalid_color_data(idx)

            combo = f"{size}_{color_key}"

            if combo in combinations:
                ProductException.duplicate_variant_combination(size, color_key)

            combinations.add(combo)


    async def validate_colors(self, variants: List[dict], session: AsyncSession):
        for idx, variant in enumerate(variants):
            color_id = variant.get("color_id")

            if color_id:
                conditions = [Color.id == color_id, Color.deleted_at.is_(None)]
                color_exists = await color_repository.get_color(session=session, where_conditions=conditions)
                if not color_exists:
                    raise ColorException.color_not_found()
            else:
                raise ProductException.invalid_color_data(idx)


    async def prepare_update_data(self, variant_ids: Set[str], new_dict: Dict, product_id: str):
        to_update_data = {}

        for variant_id in variant_ids:
            data = new_dict[variant_id]

            sku = data.get("sku")
            if not sku:
                sku = f"{str(product_id)[:8]}-{uuid.uuid4().hex[:6].upper()}"
            else:
                sku = sku.strip().upper()

            update_dict = {
                "size": data.get("size", "").strip().upper() if data.get("size") else None,
                "image": data.get("image", "").strip() if data.get("image") else None,
                "price": data["price"],
                "quantity": data["quantity"],
                "sku": sku,
                "deleted_at": None,
                "updated_at": datetime.now()
            }

            if data.get("color_id"):
                update_dict["color_id"] = data["color_id"]
                update_dict["color_name"] = None
                update_dict["color_code"] = None
            elif data.get("color_name") and data.get("color_code"):
                update_dict["color_id"] = None
                update_dict["color_name"] = data["color_name"]
                update_dict["color_code"] = data["color_code"]

            to_update_data[variant_id] = update_dict

        return to_update_data
