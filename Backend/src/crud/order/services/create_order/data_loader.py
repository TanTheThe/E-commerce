from typing import Set
from sqlalchemy.orm import selectinload
from src.database.models import User, Address, Product_Variant, Product, Color
from src.crud.address.repositories import AddressRepository
from src.crud.user.repositories import UserRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.color.repositories import ColorRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors.address import AddressException
from src.errors.product import ProductException
from src.errors.authentication import AuthException


user_repository = UserRepository()
address_repository = AddressRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()


class DataLoaderService:
    async def validate_customer_and_address(self, customer_id: str, address_id: str, session: AsyncSession):
        conditions_user = [
            User.id == customer_id,
            User.deleted_at.is_(None),
            User.customer_status == "active"
        ]
        customer = await user_repository.get_user(session=session, where_conditions=conditions_user)
        if not customer:
            AuthException.user_not_found()

        conditions_address = [
            Address.id == address_id,
            Address.deleted_at.is_(None),
            Address.user_id == customer.id
        ]

        options = [
            selectinload(Address.ward),
            selectinload(Address.province)
        ]

        address = await address_repository.get_address(session=session, where_conditions=conditions_address, options=options)

        if not address:
            AddressException.not_found()

        if not address.ward or not address.province:
            AddressException.invalid_province_ward()

        return customer, address


    async def load_variants_with_relations(self, variant_ids: Set[str], session: AsyncSession):
        condition = [Product_Variant.id.in_(variant_ids)]

        options = [
            selectinload(Product_Variant.product).options(
                selectinload(Product.special_offer),
            ).load_only(
                Product.id,
                Product.name,
                Product.images,
                Product.special_offer_id
            ),
        ]

        variants, _ = await product_variant_repository.get_all_product_variant(
            session=session,
            where_conditions=condition,
            options=options,
            for_update=True
        )

        if not variants:
            ProductException.not_found_variant()

        return {str(v.id): v for v in variants}


    async def load_colors_batch(self, color_ids: Set[str], session: AsyncSession):
        if not color_ids:
            return {}

        conditions = [
            Color.id.in_(color_ids),
            Color.deleted_at.is_(None)
        ]

        colors, _ = await color_repository.get_all_color(
            session=session,
            where_conditions=conditions
        )

        return {str(c.id): c for c in colors}