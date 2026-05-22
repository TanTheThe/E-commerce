from typing import Dict
from src.database.models import Product_Variant, Product
from src.crud.product.repositories import ProductRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from sqlalchemy import update
from src.errors.product import ProductException

product_repository = ProductRepository()

class InventoryService:
    async def update_inventory_batch(self, order_items_map: Dict[str, int],  # {variant_id: quantity}
                                     variant_map, session: AsyncSession):
        updates = []

        for variant_id, quantity in order_items_map.items():
            variant = variant_map.get(variant_id)
            if not variant:
                ProductException.not_found_variant()

            if variant.quantity < quantity:
                ProductException.out_of_stock(variant_id)

            updates.append({
                "id": str(variant.id),
                "quantity": variant.quantity - quantity
            })

        if updates:
            statement = update(Product_Variant)
            await session.execute(statement, updates)


    async def restore_inventory_batch(self, order_items_map: Dict[str, int],
                                      variant_map, session: AsyncSession):
        updates = []

        for variant_id, quantity in order_items_map.items():
            variant = variant_map.get(variant_id)
            if not variant:
                ProductException.not_found_variant()

            updates.append({
                "id": str(variant.id),
                "quantity": variant.quantity + quantity
            })

        if updates:
            statement = update(Product_Variant)
            await session.execute(statement, updates)


    async def update_product_stats(self,
                                   order_items_map: Dict[str, int],  # {variant_id: quantity}
                                   variant_map, session: AsyncSession):
        product_updates = {}

        for variant_id, quantity in order_items_map.items():
            variant = variant_map.get(variant_id)
            if not variant:
                continue

            product_id = str(variant.product_id)
            if product_id not in product_updates:
                product_updates[product_id] = {
                    "total_sold": 0,
                    "popularity_score": 0
                }

            product_updates[product_id]["total_sold"] += quantity
            product_updates[product_id]["popularity_score"] += 1

        if product_updates:
            for product_id, updates in product_updates.items():
                condition = and_(Product.id == product_id)
                await product_repository.update_product_some_field(
                    condition,
                    {
                        "total_sold": Product.total_sold + updates["total_sold"],
                        "popularity_score": Product.popularity_score + updates["popularity_score"]
                    },
                    session
                )
