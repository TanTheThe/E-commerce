from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, case
from sqlalchemy import literal, text
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product_Variant
from uuid import UUID

from src.errors.color import ColorException

product_variant_repository = ProductVariantRepository()


class ProductVariantService:
    async def update_product_variant(self, product_id: str, new_variants: list, session: AsyncSession):
        condition = and_(Product_Variant.product_id == product_id)
        existing_variants = await product_variant_repository.get_all_product_variant(condition, session)

        existing_dict = {str(v.id): v for v in existing_variants}
        new_dict = {str(v["id"]): v for v in new_variants if v.get("id")}

        # VD: v1, v2, v3
        old_ids = set(existing_dict.keys())

        # VD: v2, v4
        new_ids = set(new_dict.keys())

        # KQ: v1, v3 => Những cái cũ của product đó (ko có trong new_variants) nên cần đc loại bỏ
        to_soft_delete_ids = old_ids - new_ids

        for variant_id in to_soft_delete_ids:
            variant = existing_dict[variant_id]
            if variant.deleted_at is None:
                variant.deleted_at = datetime.now()

        to_update_data = {}
        for variant_id in new_ids & old_ids:
            data = new_dict[variant_id]

            if data.get("color_id") and (data.get("color_name") or data.get("color_code")):
                ColorException.invalid_color_format()
            if not data.get("color_id") and (not data.get("color_name") or not data.get("color_code")):
                ColorException.invalid_color_format()

            if data.get("color_id") and (not data.get("color_name") and not data.get("color_code")):
                to_update_data[UUID(variant_id)] = {
                    "size": data.get("size"),
                    "color_id": UUID(data.get("color_id")),
                    "price": data["price"],
                    "quantity": data["quantity"],
                    "sku": data["sku"],
                    "deleted_at": None,
                    "updated_at": datetime.now()
                }

            if not data.get("color_id") and (data.get("color_name") and data.get("color_code")):
                to_update_data[UUID(variant_id)] = {
                    "size": data.get("size"),
                    "color_name": data.get("color_name"),
                    "color_code": data.get("color_code"),
                    "price": data["price"],
                    "quantity": data["quantity"],
                    "sku": data["sku"],
                    "deleted_at": None,
                    "updated_at": datetime.now()
                }

        if to_update_data:
            await self._bulk_update_variants(to_update_data, session)

        to_create = [v for v in new_variants if not v.get("id")]
        if to_create:
            await self._bulk_create_variants(to_create, product_id, session)

        await session.commit()

    async def _bulk_update_variants(self, update_data: dict[UUID, dict], session: AsyncSession):
        ids = list(update_data.keys())

        def build_case(field: str):
            col = getattr(Product_Variant, field)
            cases = []

            for uid, data in update_data.items():
                field_value = data.get(field)
                if field_value is not None:
                    cases.append((Product_Variant.id == uid, field_value))
                else:
                    cases.append((Product_Variant.id == uid, None))

            return case(*cases, else_=col)

        condition = Product_Variant.id.in_(ids)
        values_dict = {
            "size": build_case("size"),
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

    async def _bulk_create_variants(self, items: list[dict], product_id: str, session: AsyncSession):
        await product_variant_repository.create_product_variant(items, product_id, session)
