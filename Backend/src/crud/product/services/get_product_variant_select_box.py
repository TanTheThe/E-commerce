from typing import List, Optional, Dict, Any
from sqlalchemy.orm import selectinload
from src.crud.color.services import ColorService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product, Product_Variant, Categories_Product, Color, Supplier_Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import case
from src.crud.product.repositories import ProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService

product_repository = ProductRepository()
product_variant_repository = ProductVariantRepository()

product_variant_service = ProductVariantService()
categories_product_service = CategoriesProductService()
color_service = ColorService()


class GetProductVariantSelectBoxService:
    async def get_products_select_box(self, session: AsyncSession, category_id: Optional[str] = None,
                                      supplier_id: Optional[str] = None) -> List[Dict[str, Any]]:
        where_conditions = [Product.deleted_at.is_(None)]

        joins = []
        if category_id:
            joins.append((
                Categories_Product,
                {
                    'on': Categories_Product.product_id == Product.id,
                    'type': 'inner'
                }
            ))
            where_conditions.extend([
                Categories_Product.categories_id == category_id,
                Categories_Product.deleted_at.is_(None)
            ])

        if supplier_id:
            joins.append((
                Supplier_Product,
                {
                    'on': Supplier_Product.product_id == Product.id,
                    'type': 'inner'
                }
            ))
            where_conditions.extend([
                Supplier_Product.supplier_id == supplier_id,
                Supplier_Product.is_active == True
            ])

        products, _ = await product_repository.get_all_product(session=session, joins=joins,
                                                               where_conditions=where_conditions, skip=0, limit=1000)

        return [
            {
                "id": str(product[0].id),
                "name": product[0].name
            }
            for product in products
        ]

    async def get_variants_select_box(self, product_id: str, session: AsyncSession) -> List[Dict[str, Any]]:
        where_conditions = [
            Product_Variant.product_id == product_id,
            Product_Variant.deleted_at.is_(None)
        ]
        joins = [(
            Color,
            {
                'on': Product_Variant.color_id == Color.id,
                'type': 'outer'
            }
        )]
        order_by = [
            case(
                (Product_Variant.color_name.isnot(None), Product_Variant.color_name),
                else_=Color.name
            ),
            Product_Variant.size
        ]
        options = [selectinload(Product_Variant.color)]
        variants, _ = await product_variant_repository.get_all_product_variant(session=session,
                                                                               where_conditions=where_conditions,
                                                                               order_by=order_by, joins=joins, skip=0,
                                                                               limit=1000,
                                                                               options=options)

        return [
            {
                "id": str(variant.id),
                "name": self.build_variant_name(variant),
                "price": variant.price
            }
            for variant in variants
        ]

    def build_variant_name(self, variant: Product_Variant) -> str:
        parts = []

        color_display = variant.color_name
        if not color_display and variant.color:
            color_display = variant.color.name

        if color_display:
            parts.append(color_display)
        if variant.size:
            parts.append(f"Size {variant.size}")

        if not parts:
            parts.append(variant.sku)

        return " - ".join(parts)
