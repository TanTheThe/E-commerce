from typing import Optional
from sqlmodel import and_, func, or_
from src.crud.brand.repositories import BrandRepository
from src.crud.material.repositories import MaterialRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.tag.repositories import TagRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Stock, Product_Variant, Brand, Material, Tag, Product, Product_Material, \
    Product_Tag
from src.errors.brand import BrandException
from src.errors.material import MaterialException
from src.errors.stock import StockException
from src.errors.tag import TagException
from src.schemas.stock import TotalInventoryFilterParams

warehouse_repository = WareHouseRepository()
stock_repository = StockRepository()
product_variant_repository = ProductVariantRepository()
brand_repository = BrandRepository()
material_repository = MaterialRepository()
tag_repository = TagRepository()


class GetTotalInventoryService:
    async def get_total_inventory(self, filters: TotalInventoryFilterParams, session: AsyncSession,
                                  skip: int = 0, limit: int = 100):
        if filters.min_quantity is not None and filters.min_quantity < 0:
            StockException.min_must_greater_than_0()

        if filters.brand_id:
            condition = and_(Brand.id == filters.brand_id, Brand.deleted_at.is_(None), Brand.is_active == True)
            brand = await brand_repository.get_brand(condition, session)
            if not brand:
                BrandException.brand_not_found()

        if filters.material_id:
            condition = and_(Material.id == filters.material_id, Material.deleted_at.is_(None),
                             Material.is_active == True)
            material = await material_repository.get_material(condition, session)
            if not material:
                MaterialException.material_not_found()

        if filters.tag_id:
            condition = and_(Tag.id == filters.tag_id, Tag.deleted_at.is_(None), Tag.is_active == True)
            tag = await tag_repository.get_tag(condition, session)
            if not tag:
                TagException.tag_not_found()

        if filters.min_quantity is not None and filters.max_quantity is not None:
            if filters.min_quantity > filters.max_quantity:
                StockException.min_must_less_than_max()

        summary = await self.get_total_inventory_summary(
            session=session,
            brand_id=filters.brand_id,
            material_id=filters.material_id,
            tag_id=filters.tag_id
        )

        products, total = await self.get_total_inventory_with_filters(
            session=session,
            brand_id=filters.brand_id,
            material_id=filters.material_id,
            tag_id=filters.tag_id,
            status=filters.status.value if filters.status else None,
            min_quantity=filters.min_quantity,
            max_quantity=filters.max_quantity,
            search=filters.search,
            skip=skip,
            limit=limit,
        )

        product_summaries = []
        for product in products:
            overall_status = self.determine_overall_status(
                product['total_quantity'],
                product['total_available']
            )

            product_summaries.append({
                "product_id": str(product['product_id']),
                "product_name": product['product_name'],
                "product_sku": product['product_sku'],
                "brand_name": product['brand_name'],
                "total_quantity": product['total_quantity'],
                "total_available": product['total_available'],
                "total_reserved": product['total_reserved'],
                "warehouses_count": product['warehouses_count'],
                "average_cost_price": product['average_cost_price'],
                "total_inventory_value": product['total_inventory_value'],
                "overall_status": overall_status
            })

        return {
            "total_products": total,
            "total_quantity_all": summary['total_quantity_all'],
            "total_available_all": summary['total_available_all'],
            "total_reserved_all": summary['total_reserved_all'],
            "total_inventory_value_all": summary['total_inventory_value_all'],
            "products": product_summaries,
        }


    async def get_total_inventory_summary(self, session: AsyncSession,
                                          brand_id: Optional[str] = None,
                                          material_id: Optional[str] = None,
                                          tag_id: Optional[str] = None) -> dict:

        select_columns = [
            func.sum(Stock.quantity).label('total_quantity'),
            func.sum(Stock.available_quantity).label('total_available'),
            func.sum(Stock.reserved_quantity).label('total_reserved'),
            func.sum(
                Stock.quantity * func.coalesce(Stock.cost_price, 0)
            ).label('total_value')
        ]

        joins = []
        if brand_id or material_id or tag_id:
            joins.extend([
                (Product_Variant, {
                    'on': Stock.product_variant_id == Product_Variant.id
                }),
                (Product, {
                    'on': Product_Variant.product_id == Product.id
                })
            ])

            if brand_id:
                joins.append((Brand, {
                    'type': 'outer',
                    'on': Product.brand_id == Brand.id
                }))

            if material_id:
                joins.append((Product_Material, {
                    'on': Product.id == Product_Material.product_id
                }))

            if tag_id:
                joins.append((Product_Tag, {
                    'on': Product.id == Product_Tag.product_id
                }))

        where_conditions = []

        if brand_id:
            where_conditions.append(Product.brand_id == brand_id)

        if material_id:
            where_conditions.append(Product_Material.material_id == material_id)

        if tag_id:
            where_conditions.append(Product_Tag.tag_id == tag_id)

        row = await stock_repository.get_aggregated_inventory_summary(
            select_columns=select_columns, session=session, joins=joins, where_conditions=where_conditions
        )

        if not row:
            return {
                'total_quantity_all': 0,
                'total_available_all': 0,
                'total_reserved_all': 0,
                'total_inventory_value_all': 0
            }

        return {
            'total_quantity_all': row.total_quantity or 0,
            'total_available_all': row.total_available or 0,
            'total_reserved_all': row.total_reserved or 0,
            'total_inventory_value_all': (
                int(row.total_value) if row.total_value else 0
            )
        }


    async def get_total_inventory_with_filters(self,
                                               session: AsyncSession,
                                               brand_id: Optional[str] = None,
                                               material_id: Optional[str] = None,
                                               tag_id: Optional[str] = None,
                                               status: Optional[str] = None,
                                               min_quantity: Optional[int] = None,
                                               max_quantity: Optional[int] = None,
                                               search: Optional[str] = None,
                                               skip: int = 0, limit: int = 10):

        select_columns = [
            Product.id.label('product_id'),
            Product.name.label('product_name'),
            Product.sku.label('product_sku'),
            Brand.name.label('brand_name'),
            func.sum(Stock.quantity).label('total_quantity'),
            func.sum(Stock.available_quantity).label('total_available'),
            func.sum(Stock.reserved_quantity).label('total_reserved'),
            func.count(func.distinct(Stock.warehouse_id)).label('warehouses_count'),
            func.avg(Stock.cost_price).label('average_cost_price'),
            func.sum(
                Stock.quantity * func.coalesce(Stock.cost_price, 0)
            ).label('total_inventory_value')
        ]

        joins = [
            (Product_Variant, {
                'on': Stock.product_variant_id == Product_Variant.id
            }),
            (Product, {
                'on': Product_Variant.product_id == Product.id
            }),
            (Brand, {
                'type': 'outer',
                'on': Product.brand_id == Brand.id
            })
        ]

        if material_id:
            joins.append((Product_Material, {
                'on': Product.id == Product_Material.product_id
            }))

        if tag_id:
            joins.append((Product_Tag, {
                'on': Product.id == Product_Tag.product_id
            }))

        where_conditions = []

        if brand_id:
            where_conditions.append(Product.brand_id == brand_id)

        if material_id:
            where_conditions.append(Product_Material.material_id == material_id)

        if tag_id:
            where_conditions.append(Product_Tag.tag_id == tag_id)

        if search:
            search_pattern = f"%{search}%"
            where_conditions.append(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.sku.ilike(search_pattern)
                )
            )

        group_by_columns = [
            Product.id,
            Product.name,
            Product.sku,
            Brand.name
        ]

        having_conditions = []

        if min_quantity is not None:
            having_conditions.append(func.sum(Stock.quantity) >= min_quantity)

        if max_quantity is not None:
            having_conditions.append(func.sum(Stock.quantity) <= max_quantity)

        order_by = func.sum(Stock.quantity).desc()

        rows, total = await stock_repository.get_aggregated_inventory_list(
            select_columns=select_columns,
            session=session,
            joins=joins,
            where_conditions=where_conditions,
            group_by_columns=group_by_columns,
            having_conditions=having_conditions,
            order_by=order_by,
            skip=skip,
            limit=limit
        )

        products = []
        for row in rows:
            products.append({
                'product_id': row.product_id,
                'product_name': row.product_name,
                'product_sku': row.product_sku,
                'brand_name': row.brand_name,
                'total_quantity': row.total_quantity or 0,
                'total_available': row.total_available or 0,
                'total_reserved': row.total_reserved or 0,
                'warehouses_count': row.warehouses_count or 0,
                'average_cost_price': (
                    int(row.average_cost_price)
                    if row.average_cost_price else None
                ),
                'total_inventory_value': (
                    int(row.total_inventory_value)
                    if row.total_inventory_value else 0
                )
            })

        return products, total

    def determine_overall_status(self, total_quantity: int, total_available: int) -> str:
        if total_quantity == 0:
            return "out_of_stock"

        available_percentage = (total_available / total_quantity) * 100 if total_quantity > 0 else 0

        if available_percentage < 20:
            return "low_stock"
        elif available_percentage < 90:
            return "partially_available"
        else:
            return "available"
