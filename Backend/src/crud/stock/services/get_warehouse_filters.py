from typing import List
from sqlalchemy import func
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.brand.repositories import BrandRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product.repositories import ProductRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import Warehouse, Categories, Product, Categories_Product, Product_Variant, Stock, Brand
from src.errors.warehouse import WareHouseException

warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
stock_repository = StockRepository()
category_product_repository = CategoriesProductRepository()
product_repository = ProductRepository()
category_repository = CategoriesRepository()
brand_repository = BrandRepository()

class GetWarehouseFiltersService:
    async def get_warehouse_filters(self, session: AsyncSession, warehouse_id: str):
        condition_warehouse = and_(
            Warehouse.id == warehouse_id,
            Warehouse.is_active == True
        )
        warehouse = await warehouse_repository.get_warehouse(condition_warehouse, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        categories = await self.get_categories_with_count(session, warehouse_id)
        brands = await self.get_brands_with_count(session, warehouse_id)
        stock_statuses = await product_variant_repository.get_stock_statuses_count(session, warehouse_id)

        return {
            "categories": categories,
            "brands": brands,
            "stock_statuses": stock_statuses
        }


    async def get_categories_with_count(self, session: AsyncSession, warehouse_id: str) -> List[dict]:
        select_columns = [
            Categories.id,
            Categories.name,
            func.count(func.distinct(Product.id)).label('product_count')
        ]

        joins = [
            (
                Categories_Product,
                {'on': Categories_Product.categories_id == Categories.id}
            ),
            (
                Product,
                {'on': Categories_Product.product_id == Product.id}
            ),
            (
                Product_Variant,
                {'on': Product_Variant.product_id == Product.id}
            ),
            (
                Stock,
                {'on': Stock.product_variant_id == Product_Variant.id}
            )
        ]

        where_conditions = [
            Stock.warehouse_id == warehouse_id,
            Categories.deleted_at.is_(None),
            Categories_Product.deleted_at.is_(None),
            Product.deleted_at.is_(None),
            Product_Variant.deleted_at.is_(None)
        ]

        group_by_columns = [Categories.id, Categories.name]

        categories, _ = await category_repository.get_all_categories(
            session=session,
            select_columns=select_columns,
            joins=joins,
            where_conditions=where_conditions,
            group_by_columns=group_by_columns,
            skip=0,
            limit=1000
        )

        return [
            {
                'id': str(row.id),
                'name': row.name,
                'product_count': int(row.product_count)
            }
            for row in categories
        ]


    async def get_brands_with_count(self, session: AsyncSession, warehouse_id: str):
        select_columns = [
            Brand.id,
            Brand.name,
            func.count(func.distinct(Product.id)).label('product_count')
        ]

        joins = [
            (
                Product,
                {'on': Product.brand_id == Brand.id}
            ),
            (
                Product_Variant,
                {'on': Product_Variant.product_id == Product.id}
            ),
            (
                Stock,
                {'on': Stock.product_variant_id == Product_Variant.id}
            )
        ]

        where_conditions = [
            Stock.warehouse_id == warehouse_id,
            Brand.deleted_at.is_(None),
            Brand.is_active == True,
            Product.deleted_at.is_(None),
            Product_Variant.deleted_at.is_(None)
        ]

        group_by_columns = [Brand.id, Brand.name]

        brands, _ = await brand_repository.get_all_brand(
            session=session,
            select_columns=select_columns,
            joins=joins,
            where_conditions=where_conditions,
            group_by_columns=group_by_columns,
            skip=0,
            limit=1000
        )

        return [
            {
                'id': str(row.id),
                'name': row.name,
                'product_count': int(row.product_count)
            }
            for row in brands
        ]







