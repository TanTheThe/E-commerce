from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.color.repositories import ColorRepository
from src.crud.product.repositories import ProductRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.product_variant.services import ProductVariantService
from src.database.models import Product, Product_Variant, Order_Detail, Order, Color
from src.errors.color import ColorException
from src.errors.product import ProductException

product_variant_repository = ProductVariantRepository()
product_variant_service = ProductVariantService()
product_repository = ProductRepository()
color_repository = ColorRepository()

class ProductVariantManager:
    async def delete_variants(self, product_id: str, deleted_ids: List[str], product: Product, session: AsyncSession):
        existing_variant_ids = [str(v.id) for v in product.product_variant if v.deleted_at is None]
        invalid_ids = set(deleted_ids) - set(existing_variant_ids)
        if invalid_ids:
            ProductException.variant_not_belong_to_product(list(invalid_ids))

        for variant_id in deleted_ids:
            has_pending = await self.check_variant_in_pending_orders(variant_id, session)
            if has_pending:
                ProductException.variant_in_pending_order(variant_id)

        await product_variant_repository.bulk_delete_product_variants(deleted_ids, session)

    async def update_variants(self, product_id: str, variants: List[dict], session: AsyncSession):
        await self.validate_variants(variants, product_id, session)
        await product_variant_service.update_product_variant(product_id, variants, session)


    async def check_variant_in_pending_orders(self, variant_id: str, session: AsyncSession):
        joins = [
            (Order_Detail, {"type": "inner", "on": Order_Detail.product_id == Product.id}),
            (Order, {"type": "inner", "on": Order.id == Order_Detail.order_id}),
        ]
        conditions = [
            Order_Detail.product_variant_id == variant_id,
            Order.status.in_(["pending", "processing", "confirmed"]),
        ]
        product = await product_repository.get_product(
            session=session, select_columns=[Product.id],
            joins=joins, where_conditions=conditions
        )
        return product is not None


    async def validate_variants(self, variants: List[dict], product_id: str, session: AsyncSession):
        if not variants or len(variants) == 0:
            ProductException.variants_required()

        skus = []
        for idx, variant in enumerate(variants):
            price = variant.get('price')
            if price is not None and (not isinstance(price, int) or price <= 0):
                ProductException.invalid_price(idx)

            quantity = variant.get('quantity')
            if quantity is not None and (not isinstance(quantity, int) or quantity < 0):
                ProductException.invalid_quantity(idx)

            sku = variant.get('sku')
            if sku:
                if sku in skus:
                    raise ProductException.duplicate_sku()
                skus.append(sku)

                conditions = [
                    Product_Variant.sku == sku,
                    Product_Variant.product_id != product_id,
                    Product_Variant.deleted_at.is_(None),
                ]
                existing = await product_variant_repository.get_product_variant(
                    session=session, where_conditions=conditions
                )
                if existing:
                    raise ProductException.sku_already_exists()

            size = variant.get('size')
            if size and not isinstance(size, str):
                raise ProductException.invalid_size(idx)

            color_id = variant.get('color_id')
            if color_id:
                conditions = [Color.id == color_id, Color.deleted_at.is_(None)]
                color_exists = await color_repository.get_color(session=session, where_conditions=conditions)
                if not color_exists:
                    raise ColorException.color_not_found()