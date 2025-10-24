from datetime import datetime
from src.crud.cart.repositories import CartRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product_Variant, Product, Special_Offer, Cart, Cart_Item
from src.errors.cart import CartException
from src.errors.product import ProductException
from src.schemas.cart import CartCreateModel, CartItemCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from sqlalchemy.orm import selectinload

cart_repository = CartRepository()
product_variant_repository = ProductVariantRepository()


class CreateCartService:
    async def create_cart(self, user_id: str, cart_data: CartCreateModel, session: AsyncSession):
        condition_variant = and_(
            Product_Variant.id == cart_data.product_variant_id,
            Product_Variant.deleted_at.is_(None)
        )

        joins_variant = [
            selectinload(Product_Variant.product).options(
                selectinload(Product.special_offer).load_only(
                    Special_Offer.id,
                    Special_Offer.discount,
                    Special_Offer.type,
                    Special_Offer.used_quantity,
                    Special_Offer.total_quantity,
                    Special_Offer.start_time,
                    Special_Offer.end_time,
                    Special_Offer.deleted_at
                )
            ).load_only(
                Product.id,
                Product.name,
                Product.images,
                Product.special_offer_id,
                Product.status,
                Product.deleted_at
            ),
        ]

        product_variant = await product_variant_repository.get_product_variant(condition_variant, session,
                                                                               joins_variant)

        if not product_variant:
            ProductException.not_found_variant()

        if product_variant.quantity is None or product_variant.quantity < 0:
            ProductException.not_found_variant()

        if product_variant.price is None or product_variant.price <= 0:
            ProductException.not_found_variant()

        product = product_variant.product
        if not product or product.deleted_at is not None or product.status != "active":
            ProductException.not_found()

        condition_user_id = [
            Cart.user_id == user_id,
            Cart.deleted_at.is_(None)
        ]

        joins_user_id = [
            selectinload(Cart.items).options(
                selectinload(Cart_Item.product).load_only(
                    Product.id,
                    Product.name,
                    Product.deleted_at,
                    Product.status
                ),
                selectinload(Cart_Item.product_variant).load_only(
                    Product_Variant.id,
                    Product_Variant.size,
                    Product_Variant.color_id,
                    Product_Variant.color_name,
                    Product_Variant.color_code,
                    Product_Variant.sku,
                    Product_Variant.image,
                    Product_Variant.deleted_at
                ),
            ).load_only(
                Cart_Item.id,
                Cart_Item.product_id,
                Cart_Item.product_variant_id,
                Cart_Item.quantity,
                Cart_Item.price,
                Cart_Item.deleted_at
            ),
        ]

        cart = await cart_repository.get_cart(condition_user_id, session, joins_user_id)

        if not cart:
            cart = await cart_repository.create_cart(user_id, session)
            if not cart:
                CartException.fail_create_cart()

        original_price = product_variant.price
        special_offer = product.special_offer
        discounted_price = await self.calculate_discounted_price(original_price, special_offer, session)

        if discounted_price < 0:
            discounted_price = 0

        condition_check_variant_cart = [
            Cart_Item.product_variant_id == cart_data.product_variant_id,
            Cart_Item.cart_id == cart.id,
            Cart_Item.deleted_at.is_(None)
        ]

        existing_cart_item = await cart_repository.get_cart_item(condition_check_variant_cart, session)

        if existing_cart_item:
            new_quantity = existing_cart_item.quantity + cart_data.quantity

            if new_quantity > product_variant.quantity:
                ProductException.not_enough_variant()

            condition_update_cart_item = and_(Cart_Item.id == existing_cart_item.id)
            await cart_repository.update_cart_item(
                condition_update_cart_item,
                {
                    "quantity": new_quantity,
                    "price": discounted_price,
                    "updated_at": datetime.now()
                },
                session
            )
        else:
            if cart_data.quantity > product_variant.quantity:
                ProductException.not_enough_variant()

            cart_item_create = CartItemCreateModel(
                cart_id=cart.id,
                product_id=product.id,
                product_variant_id=product_variant.id,
                quantity=cart_data.quantity,
                price=discounted_price
            )

            cart_item = await cart_repository.create_cart_item(cart_item_create, session)
            if not cart_item:
                CartException.fail_create_cart()

        await session.commit()

        condition_cart_response = [
            Cart.id == cart.id,
            Cart.deleted_at.is_(None)
        ]

        joins_cart_response = [
            selectinload(Cart.user),
            selectinload(Cart.items).options(
                selectinload(Cart_Item.product).load_only(
                    Product.id,
                    Product.name,
                    Product.deleted_at,
                    Product.status
                ),
                selectinload(Cart_Item.product_variant).load_only(
                    Product_Variant.id,
                    Product_Variant.size,
                    Product_Variant.color_id,
                    Product_Variant.color_name,
                    Product_Variant.color_code,
                    Product_Variant.sku,
                    Product_Variant.image,
                    Product_Variant.deleted_at
                ),
            ).load_only(
                Cart_Item.id,
                Cart_Item.product_id,
                Cart_Item.product_variant_id,
                Cart_Item.quantity,
                Cart_Item.price,
                Cart_Item.deleted_at
            )
        ]
        final_cart = await cart_repository.get_cart(condition_cart_response, session, joins_cart_response)

        return await self.format_cart_response(final_cart, session)

    async def calculate_discounted_price(self, original_price, special_offer: Special_Offer, session: AsyncSession):
        if original_price is None or original_price <= 0:
            return 0

        valid_offer = self._is_offer_valid(special_offer)

        if not valid_offer:
            return original_price

        if not special_offer.discount or special_offer.discount <= 0:
            return original_price

        if special_offer.type == "percent":
            discount_percent = min(special_offer.discount, 100)
            discount_amount = (original_price * discount_percent) / 100
            final_price = original_price - discount_amount
        elif special_offer.type == "fixed":
            final_price = max(0, original_price - special_offer.discount)
        else:
            return original_price

        final_price = int(round(final_price / 1000) * 1000)

        return max(0, int(final_price))

    async def format_cart_response(self, cart: Cart, session: AsyncSession):
        items = []
        for cart_item in cart.items:
            if cart_item.deleted_at is not None:
                continue

            if not cart_item.id or not cart_item.product_variant_id:
                continue

            if cart_item.quantity is None or cart_item.quantity <= 0:
                continue

            if cart_item.price is None or cart_item.price < 0:
                continue

            product = cart_item.product
            if not product or product.deleted_at is not None or product.status != "active":
                continue

            product_variant = cart_item.product_variant
            if not product_variant or product_variant.deleted_at is not None:
                continue

            item_data = {
                "item_id": str(cart_item.id),
                "product_id": str(cart_item.product_id),
                "product_name": product.name if product.name else "Unknown Product",
                "product_variant_id": str(cart_item.product_variant_id),
                "size": product_variant.size if product_variant.size else None,
                "color_id": str(product_variant.color_id) if product_variant.color_id else None,
                "color_name": product_variant.color_name if product_variant.color_name else None,
                "color_code": product_variant.color_code if product_variant.color_code else None,
                "sku": product_variant.sku if product_variant.sku else None,
                "image": product_variant.image if product_variant.image else None,
                "quantity": cart_item.quantity,
                "unit_price": cart_item.price,
                "total_item_price": cart_item.price * cart_item.quantity,
            }

            items.append(item_data)
        return {
            "cart_id": str(cart.id),
            "user_id": str(cart.user_id),
            "created_at": cart.created_at.isoformat() if cart.created_at else "",
            "items_count": len(items),
            "items": items
        }

    def _is_offer_valid(self, offer: Special_Offer) -> bool:
        if not offer:
            return False

        if offer.deleted_at is not None:
            return False

        now = datetime.now()
        if offer.start_time > now or offer.end_time < now:
            return False

        if offer.used_quantity >= offer.total_quantity:
            return False

        return True
