from typing import Optional, List
from sqlalchemy import func, Integer
from sqlmodel import and_, select, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import Warehouse, Product_Variant, Stock, Product, Brand, Categories_Product, Categories
from src.errors.warehouse import WareHouseException
from src.schemas.stock import ProductStockStatus, SortBy, SortOrder

warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
stock_repository = StockRepository()
category_product_repository = CategoriesProductRepository()

class GetProductsInWarehouseService:
    async def get_products_summary(self, session: AsyncSession,
                                   warehouse_id: str,
                                   skip: int = 0, limit: int = 10,
                                   search: Optional[str] = None,
                                   category_ids: Optional[List[str]] = None,
                                   brand_ids: Optional[List[str]] = None,
                                   stock_status: ProductStockStatus = ProductStockStatus.ALL,
                                   sort_by: SortBy = SortBy.NAME,
                                   sort_order: SortOrder = SortOrder.ASC):
        condition = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        select_columns_stock_summary = [
            Product_Variant.product_id,
            func.sum(Stock.quantity).label('total_quantity'),
            func.sum(Stock.available_quantity).label('total_available'),
            func.sum(Stock.reserved_quantity).label('total_reserved'),
            func.count(func.distinct(Product_Variant.id)).label('total_variants'),
            func.sum(func.cast(Stock.quantity > 0, Integer)).label('variants_in_stock'),
            func.sum(func.cast(
                and_(
                    Stock.quantity > 0,
                    Stock.min_stock_level.isnot(None),
                    Stock.available_quantity <= Stock.min_stock_level
                ),
                Integer
            )).label('variants_low_stock'),
            func.sum(func.cast(Stock.quantity == 0, Integer)).label('variants_out_of_stock'),
            func.avg(Stock.cost_price).label('avg_cost_price'),
            func.max(Stock.last_inbound_date).label('last_inbound_date')
        ]

        stock_summary = (
            select(*select_columns_stock_summary)
            .select_from(Product_Variant)
            .join(Stock, Stock.product_variant_id == Product_Variant.id)
            .where(and_(
                Stock.warehouse_id == warehouse_id,
                Product_Variant.deleted_at.is_(None)
            ))
            .group_by(Product_Variant.product_id)
        ).subquery()

        select_cols = [
            Product.id.label('product_id'),
            Product.name.label('product_name'),
            Product.images.label('product_images'),
            Product.brand_id,
            Brand.name.label('brand_name'),
            stock_summary.c.total_quantity,
            stock_summary.c.total_available,
            stock_summary.c.total_reserved,
            stock_summary.c.total_variants,
            stock_summary.c.variants_in_stock,
            stock_summary.c.variants_low_stock,
            stock_summary.c.variants_out_of_stock,
            stock_summary.c.avg_cost_price,
            stock_summary.c.last_inbound_date
        ]

        subqueries_dict = {
            'stock_summary': {
                'subquery': stock_summary,
                'join_condition': Product.id == stock_summary.c.product_id,
                'join_type': 'inner'
            }
        }

        joins_list = [
            (Brand, {'on': Product.brand_id == Brand.id, 'type': 'outer'})
        ]

        where_conds = [Product.deleted_at.is_(None)]

        if search:
            where_conds.append(or_(
                Product.name.ilike(f"%{search}%"),
                Product.slug.ilike(f"%{search}%")
            ))

        if category_ids:
            category_subquery = select(Categories_Product.product_id).where(
                and_(
                    Categories_Product.categories_id.in_(category_ids),
                    Categories_Product.deleted_at.is_(None)
                )
            )
            where_conds.append(Product.id.in_(category_subquery))

        if brand_ids:
            where_conds.append(Product.brand_id.in_(brand_ids))

        if stock_status == ProductStockStatus.AVAILABLE:
            where_conds.append(stock_summary.c.total_available > 0)
        elif stock_status == ProductStockStatus.LOW:
            where_conds.append(stock_summary.c.variants_low_stock > 0)
        elif stock_status == ProductStockStatus.OUT:
            where_conds.append(stock_summary.c.variants_out_of_stock > 0)

        if sort_by == SortBy.NAME:
            order_col = Product.name
        elif sort_by == SortBy.TOTAL_QUANTITY:
            order_col = stock_summary.c.total_quantity
        else:
            order_col = stock_summary.c.last_inbound_date

        order_by_clause = order_col.desc() if sort_order == SortOrder.DESC else order_col.asc()

        results, total = await warehouse_repository.get_all_warehouse(
            session=session,
            select_columns=select_cols,
            select_from=Product,
            subqueries=subqueries_dict,
            joins=joins_list,
            where_conditions=where_conds,
            order_by=order_by_clause,
            skip=skip,
            limit=limit
        )

        products_data = []
        for row in results:
            categories = await self.get_product_categories(session, str(row.product_id))
            status = self.determine_stock_status(
                row.total_available or 0,
                row.variants_low_stock or 0,
                row.variants_out_of_stock or 0,
                row.total_variants or 0
            )

            thumbnail = None
            if row.product_images and len(row.product_images) > 0:
                thumbnail = row.product_images[0]

            products_data.append({
                'id': str(row.product_id),
                'name': row.product_name,
                'thumbnail': thumbnail,
                'brand': {
                    'id': str(row.brand_id) if row.brand_id else None,
                    'name': row.brand_name
                } if row.brand_id else None,
                'categories': categories,
                'stock_summary': {
                    'total_quantity': int(row.total_quantity or 0),
                    'total_available': int(row.total_available or 0),
                    'total_reserved': int(row.total_reserved or 0),
                    'total_variants': int(row.total_variants or 0),
                    'variants_in_stock': int(row.variants_in_stock or 0),
                    'variants_low_stock': int(row.variants_low_stock or 0),
                    'variants_out_of_stock': int(row.variants_out_of_stock or 0),
                    'status': status,
                    'avg_cost_price': float(row.avg_cost_price) if row.avg_cost_price else None,
                    'last_inbound_date': row.last_inbound_date.isoformat() if row.last_inbound_date else None
                }
            })

        return {
            'data': products_data,
            'total': total
        }


    async def get_product_categories(self, session: AsyncSession, product_id: str) -> List[dict]:
        select_columns = [Categories.id, Categories.name]
        select_from = Categories_Product
        joins = [
            (
                Categories,
                {'on': Categories_Product.categories_id == Categories.id}
            )
        ]
        where_conditions = [
            Categories_Product.product_id == product_id,
            Categories_Product.deleted_at.is_(None),
            Categories.deleted_at.is_(None)
        ]

        cate_products, _ = await category_product_repository.get_all_cate_product(
            session=session,
            select_columns=select_columns,
            select_from=select_from,
            joins=joins,
            where_conditions=where_conditions,
            skip=0,
            limit=1000
        )

        categories = [{'id': row.id, 'name': row.name} for row in cate_products]
        return categories


    def determine_stock_status(self, total_available: int, variants_low_stock: int,
                                variants_out_of_stock: int, total_variants: int) -> str:
        if variants_out_of_stock == total_variants:
            return "out"
        elif variants_low_stock > 0:
            return "low"
        elif total_available > 0:
            return "available"
        return "out"





