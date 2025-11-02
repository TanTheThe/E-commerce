from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product.repositories import ProductRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import Warehouse, Product_Variant, Stock, Product, Color
from src.errors.product import ProductException
from src.errors.warehouse import WareHouseException

warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
stock_repository = StockRepository()
category_product_repository = CategoriesProductRepository()
product_repository = ProductRepository()

class GetVariantsInWarehouseService:
    async def get_product_variants_detail(self, session: AsyncSession, warehouse_id: str, product_id: str):
        condition = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        product_condition = and_(Product.id == product_id, Product.deleted_at.is_(None), Product.status == "active")
        product_tuple = await product_repository.get_product(product_condition, session)
        product = product_tuple[0]
        if not product:
            ProductException.not_found()

        select_cols = [
            Product_Variant.id.label('variant_id'),
            Product_Variant.sku,
            Product_Variant.size,
            Product_Variant.color_name,
            Product_Variant.color_code,
            Product_Variant.image,
            Product_Variant.price,
            Stock.id.label('stock_id'),
            Stock.quantity,
            Stock.reserved_quantity,
            Stock.available_quantity,
            Stock.min_stock_level,
            Stock.max_stock_level,
            Stock.cost_price,
            Stock.last_cost_price,
            Stock.last_inbound_date,
            Stock.last_outbound_date,
            Color.name.label('color_table_name'),
            Color.code.label('color_table_code')
        ]

        joins_list = [
            (Stock, {'on': Stock.product_variant_id == Product_Variant.id, 'type': 'inner'}),
            (Color, {'on': Color.id == Product_Variant.color_id, 'type': 'outer'})
        ]

        where_conds = [
            Product_Variant.product_id == product_id,
            Stock.warehouse_id == warehouse_id,
            Product_Variant.deleted_at.is_(None)
        ]

        results, _ = await product_variant_repository.get_all_product_variant(
            session=session,
            select_columns=select_cols,
            joins=joins_list,
            where_conditions=where_conds,
            skip=0,
            limit=1000
        )

        variants = []
        for row in results:
            stock_status = self.determine_variant_status(
                row.quantity,
                row.available_quantity,
                row.min_stock_level
            )

            variants.append({
                'id': str(row.variant_id),
                'sku': row.sku,
                'size': row.size,
                'color_name': row.color_name if row.color_name else row.color_table_name,
                'color_code': row.color_code if row.color_code else row.color_table_code,
                'image': row.image,
                'price': float(row.price) if row.price else None,
                'stock': {
                    'id': str(row.stock_id),
                    'quantity': int(row.quantity),
                    'reserved_quantity': int(row.reserved_quantity),
                    'available_quantity': int(row.available_quantity),
                    'min_stock_level': int(row.min_stock_level) if row.min_stock_level else None,
                    'max_stock_level': int(row.max_stock_level) if row.max_stock_level else None,
                    'cost_price': float(row.cost_price) if row.cost_price else None,
                    'last_cost_price': float(row.last_cost_price) if row.last_cost_price else None,
                    'status': stock_status,
                    'last_inbound_date': row.last_inbound_date.isoformat() if row.last_inbound_date else None,
                    'last_outbound_date': row.last_outbound_date.isoformat() if row.last_outbound_date else None
                }
            })

        return {
            'product_id': str(product_id),
            'product_name': product.name,
            'variants': variants
        }


    def determine_variant_status(self, quantity: int, available_quantity: int,
                                  min_stock_level: Optional[int]) -> str:
        if quantity == 0:
            return "out"
        elif min_stock_level is not None and available_quantity <= min_stock_level:
            return "low"
        return "available"






