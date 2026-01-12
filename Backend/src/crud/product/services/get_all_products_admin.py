from sqlalchemy.orm import selectinload, joinedload
from src.crud.color.services import ColorService
from src.crud.product.services.utils import UtilProductsService
from src.database.models import Product, Categories, Product_Variant, Special_Offer, Brand, Material, Product_Material
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product.repositories import ProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.schemas.product import ProductFilterModel

product_repository = ProductRepository()

product_variant_service = ProductVariantService()
categories_product_service = CategoriesProductService()
color_service = ColorService()
utils_service = UtilProductsService()


class GetAllProductsAdminService:
    async def get_all_product_admin(self, filter_data: ProductFilterModel, session: AsyncSession, skip: int = 0,
                                    limit: int = 10, include_status: bool = True):

        options = [
            selectinload(Product.categories).options(
                joinedload(Categories.parent)
            ).load_only(
                Categories.id,
                Categories.name,
                Categories.parent_id,
                Categories.deleted_at
            ),
            selectinload(Product.product_variant).load_only(
                Product_Variant.id,
                Product_Variant.price,
                Product_Variant.quantity,
                Product_Variant.size,
                Product_Variant.color_id,
                Product_Variant.color_name,
                Product_Variant.deleted_at
            ),
            selectinload(Product.special_offer).load_only(
                Special_Offer.id,
                Special_Offer.name,
                Special_Offer.discount,
                Special_Offer.type,
                Special_Offer.used_quantity,
                Special_Offer.total_quantity,
                Special_Offer.start_time,
                Special_Offer.end_time,
                Special_Offer.deleted_at
            ),
            selectinload(Product.brand).load_only(
                Brand.id,
                Brand.name,
                Brand.slug,
                Brand.logo,
                Brand.deleted_at
            ),
            selectinload(Product.materials).load_only(
                Material.id,
                Material.name,
                Material.slug,
                Material.deleted_at
            ),
            selectinload(Product.product_materials).load_only(
                Product_Material.id,
                Product_Material.material_id,
                Product_Material.percentage,
                Product_Material.deleted_at
            ),
        ]

        filters, order_by_clause = await utils_service.filter_product(filter_data, session)

        products, total = await product_repository.get_all_product(
            session=session,
            where_conditions=filters,
            skip=skip,
            limit=limit,
            order_by=order_by_clause,
            options=options
        )

        product_list = []
        for product in products:
            p = product[0]

            valid_categories = [
                cat for cat in p.categories
                if cat.deleted_at is None
            ]

            active_variants = [
                variant for variant in p.product_variant
                if (variant.deleted_at is None and
                    variant.price is not None and variant.price >= 0 and
                    variant.quantity is not None and variant.quantity >= 0)
            ]

            variant_count = len(active_variants)
            total_stock = sum(v.quantity for v in active_variants)

            price_range = None
            if active_variants:
                prices = [v.price for v in active_variants if v.price > 0]
                if prices:
                    price_range = {
                        "min": min(prices),
                        "max": max(prices)
                    }

            offer = p.special_offer
            offer_status = utils_service.get_offer_status(offer)

            brand_data = None
            if p.brand and p.brand.deleted_at is None:
                brand_data = {
                    "id": str(p.brand.id),
                    "name": p.brand.name,
                    "slug": p.brand.slug,
                    "logo": p.brand.logo
                }

            materials_data = []
            if p.product_materials:
                for product_material in p.product_materials:
                    if product_material.deleted_at is None:
                        material = next(
                            (m for m in product.materials
                             if m.id == product_material.material_id and m.deleted_at is None),
                            None
                        )
                        if material:
                            materials_data.append({
                                "id": str(material.id),
                                "name": material.name,
                                "slug": material.slug,
                                "percentage": product_material.percentage
                            })

            product_data = {
                "id": str(p.id),
                "name": p.name,
                "images": p.images if p.images else [],
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                        "parent_id": str(category.parent_id) if category.parent_id else None
                    }
                    for category in valid_categories
                ],
                "brand": brand_data,
                "materials": materials_data,
                "created_at": str(p.created_at) if p.created_at else "",
                "variant_count": variant_count,
                "price_range": price_range,
                "avg_rating": p.avg_rating if p.avg_rating is not None else 0,
                "offer_name": offer.name if offer else None,
                "offer_valid": offer_status["is_valid"] if offer else None,
                "offer_invalid_reason": offer_status["reason"] if offer and not offer_status["is_valid"] else None,
            }

            if include_status:
                product_data["status"] = p.status if p.status else "inactive"

            product_list.append(product_data)

        return {
            "data": product_list,
            "total": total[0]
        }

    