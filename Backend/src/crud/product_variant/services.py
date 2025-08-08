from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, case
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product_Variant
from uuid import UUID

product_variant_repository = ProductVariantRepository()

class ProductVariantService:
    async def update_product_variant(self, product_id: str, new_variants: list, session: AsyncSession):
        condition = and_(Product_Variant.product_id == product_id)
        existing_variants = await product_variant_repository.get_all_product_variant(condition, session)

        existing_dict  = {str(v.id): v for v in existing_variants}
        new_dict = {str(v["id"]): v for v in new_variants if v.get("id") is not None}

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

            to_update_data[UUID(variant_id)] = {
                "size": data.get("size"),
                "color": data.get("color"),
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
            return case(
                *((Product_Variant.id == uid, data[field]) for uid, data in update_data.items()),
                else_=getattr(Product_Variant, field)
            )

        condition = Product_Variant.id.in_(ids)
        values_dict = {
            "size": build_case("size"),
            "color": build_case("color"),
            "price": build_case("price"),
            "quantity": build_case("quantity"),
            "sku": build_case("sku"),
            "deleted_at": build_case("deleted_at"),
            "updated_at": build_case("updated_at"),
        }
        await product_variant_repository.update_product_variant(values_dict, condition, session)


    async def _bulk_create_variants(self, items: list[dict], product_id: str, session: AsyncSession):
        await product_variant_repository.create_product_variant(items, product_id, session)



