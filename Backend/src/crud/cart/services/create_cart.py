from datetime import datetime
from src.crud.cart.repositories import CartRepository
from src.crud.cart.services.cart_cache import CartCacheService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product_Variant, Product, Special_Offer, Cart, Cart_Item
from src.errors.cart import CartException
from src.errors.product import ProductException
from src.schemas.cart import CartCreateModel, CartItemCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
import logging

cart_repository = CartRepository()
product_variant_repository = ProductVariantRepository()
cart_cache_service = CartCacheService()

logger = logging.getLogger(__name__)

MAX_CART_ITEMS = 50
MAX_QUANTITY_PER_ITEM = 999


class CreateCartService:
    async def create_cart(self, user_id: str, cart_data: CartCreateModel, session: AsyncSession):
        try:
            product_variant = await self.validate_product_variant(cart_data.product_variant_id, session)
            
            cart = await self.get_or_create_cart(user_id, session)
            
            await self.validate_cart_constraints(cart, cart_data.quantity)
            
            discounted_price = await self.calculate_discounted_price(product_variant.price, 
                                                                    product_variant.product.special_offer, session)
                
            await self.add_or_update_cart_item(
                cart=cart,
                product_variant=product_variant,
                cart_data=cart_data,
                discounted_price=discounted_price,
                session=session
            )

            await session.commit()
            
            await cart_cache_service.invalidate_user_cart_cache(user_id)
            logger.info(f"Cache invalidated for user {user_id} after cart creation")

            final_cart = await self.get_cart_with_details(str(cart.id), session)
            return await self.format_cart_response(final_cart, session)
        
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error in create_cart for user {user_id}: {str(e)}")
            CartException.database_constraint_violation()
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create cart for user {user_id}: {str(e)}")
            raise


    async def validate_product_variant(self, variant_id: str, session: AsyncSession):
        condition_variant = [
            Product_Variant.id == variant_id,
            Product_Variant.deleted_at.is_(None)
        ]

        options = [
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

        product_variant = await product_variant_repository.get_product_variant(session=session, where_conditions=condition_variant,
                                                                               options=options)

        if not product_variant:
            ProductException.not_found_variant()

        if product_variant.quantity is None or product_variant.quantity < 0:
            ProductException.variant_sold_out()

        if product_variant.price is None or product_variant.price <= 0:
            ProductException.invalid_variant_price()

        product = product_variant.product
        if not product or product.deleted_at is not None or product.status != "active":
            ProductException.not_found()
            
        return product_variant
    
    
    async def get_or_create_cart(self, user_id: str, session: AsyncSession):
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

        cart = await cart_repository.get_cart(session=session, where_conditions=condition_user_id, options=joins_user_id)

        if not cart:
            try:
                cart = await cart_repository.create_cart(user_id, session)
                if not cart:
                    CartException.fail_create_cart()
            except IntegrityError:
                logger.info(f"Race condition detected when creating cart for user {user_id}, retrying...")
                await session.rollback()
                
                cart = await cart_repository.get_cart(session=session, where_conditions=condition_user_id, options=joins_user_id)
                if not cart:
                    raise CartException.fail_create_cart()
        
        return cart

    async def validate_cart_constraints(self, cart, new_quantity: int):
        active_items = [
            item for item in cart.items
            if item.deleted_at is None
        ]
        
        if len(active_items) >= MAX_CART_ITEMS:
            CartException.cart_items_limit_exceeded(MAX_CART_ITEMS)
                
    async def calculate_discounted_price(self, original_price: int, special_offer: Special_Offer, session: AsyncSession):
        if original_price is None or original_price <= 0:
            return 0

        valid_offer = self.is_offer_valid(special_offer)

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

    async def add_or_update_cart_item(self, cart, product_variant, cart_data: CartCreateModel, discounted_price: int, session: AsyncSession):
        condition_check_variant_cart = [
            Cart_Item.product_variant_id == cart_data.product_variant_id,
            Cart_Item.cart_id == cart.id,
            Cart_Item.deleted_at.is_(None)
        ]
        
        existing_cart_item = await cart_repository.get_cart_item(session=session, where_conditions=condition_check_variant_cart)

        if existing_cart_item:
            new_quantity = existing_cart_item.quantity + cart_data.quantity

            if new_quantity > product_variant.quantity:
                ProductException.not_enough_variant()

            condition_update = and_(Cart_Item.id == existing_cart_item.id)
            await cart_repository.update_cart_item(
                condition_update,
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
                product_id=product_variant.product.id,
                product_variant_id=product_variant.id,
                quantity=cart_data.quantity,
                price=discounted_price
            )

            cart_item = await cart_repository.create_cart_item(cart_item_create, session)
            if not cart_item:
                CartException.fail_create_cart()
    
    async def get_cart_with_details(self, cart_id: str, session: AsyncSession):
        condition_cart_response = [
            Cart.id == cart_id,
            Cart.deleted_at.is_(None)
        ]

        joins_cart_response = [
            selectinload(Cart.user),
            selectinload(Cart.items.and_(Cart_Item.deleted_at.is_(None))).options(
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

        return await cart_repository.get_cart(
            session=session,
            where_conditions=condition_cart_response,
            options=joins_cart_response
        )
    
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

    def is_offer_valid(self, offer: Special_Offer) -> bool:
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
