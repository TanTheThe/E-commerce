from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product_Variant
from src.errors.product import ProductException


product_variant_repository = ProductVariantRepository()

class ProductUpdateValidator:
    def validate_basic_fields(self, data: dict):
        name = data.get('name')
        if name is not None:
            if not isinstance(name, str) or len(name.strip()) == 0:
                ProductException.invalid_name()
            if len(name) > 255:
                raise ProductException.name_too_long()

        description = data.get('description')
        if description is not None and not isinstance(description, str):
            raise ProductException.invalid_description()

        images = data.get('images')
        if images is not None:
            if not isinstance(images, list):
                raise ProductException.invalid_images()
            if len(images) > 10:
                raise ProductException.too_many_images()


    async def validate_has_active_variants(self, product_id: str, session: AsyncSession):
        variant = await product_variant_repository.get_product_variant(
            session=session,
            select_columns=[Product_Variant.id],
            where_conditions=[
                Product_Variant.product_id == product_id,
                Product_Variant.deleted_at.is_(None),
            ],
        )
        if variant is None:
            raise ProductException.no_active_variants()