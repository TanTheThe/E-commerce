from typing import List
from src.crud.cart.repositories import CartRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import Product_Variant, Product, Cart, Cart_Item
from src.errors.cart import CartException
from src.schemas.cart import CartItemsDeleteModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)
cart_repository = CartRepository()
product_variant_repository = ProductVariantRepository()


class RemoveCartItemsService:
    async def remove_items_from_cart(self, user_id: str, data: CartItemsDeleteModel, session: AsyncSession):
        try:
            cart = await self.get_user_cart(user_id, session)
            if not cart:
                raise CartException.cart_not_found()
            
            cart_items = await self.get_cart_items_to_delete(
                cart_id=cart.id,
                item_ids=data.item_ids,
                session=session
            )
            
            deletion_result = await self.validate_and_delete_items(
                cart_items=cart_items,
                requested_ids=data.item_ids,
                session=session
            )
            
            await session.commit()
            
            return self.format_deletion_response(deletion_result, data.item_ids)
        
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to remove items from cart for user {user_id}: {str(e)}")
            raise


    async def get_user_cart(self, user_id: str, session: AsyncSession):
        condition_check_user_cart = [Cart.user_id == user_id, Cart.deleted_at.is_(None)]
        cart = await cart_repository.get_cart(session=session, where_conditions=condition_check_user_cart)
        
        return cart
    
    
    async def get_cart_items_to_delete(self, cart_id: str, item_ids: List[str], session: AsyncSession):
        condition_get_all_cart_item = [
            Cart_Item.cart_id == cart_id,
            Cart_Item.id.in_(item_ids),
            Cart_Item.deleted_at.is_(None)
        ]

        joins_get_all_cart_item = [
            joinedload(Cart_Item.product).load_only(
                Product.id,
                Product.name,
                Product.status,
                Product.deleted_at
            ),
            joinedload(Cart_Item.product_variant).load_only(
                Product_Variant.id,
                Product_Variant.size,
                Product_Variant.color_name,
                Product_Variant.deleted_at
            ),
        ]
        
        cart_items = await cart_repository.get_all_cart_items(
            session=session,
            where_conditions=condition_get_all_cart_item,
            options=joins_get_all_cart_item
        )

        return cart_items or []
    
    
    async def validate_and_delete_items(self, cart_items: List[Cart_Item], requested_ids: List[str], session: AsyncSession):
        if not cart_items:
            logger.warning(f"No valid items found for deletion from requested IDs")
            return {
                'deleted_count': 0,
                'valid_item_ids': [],
                'invalid_item_ids': requested_ids,
                'not_found_item_ids': requested_ids
            }
        
        valid_item_ids = [str(item.id) for item in cart_items]
        valid_item_ids_set = set(valid_item_ids)
        requested_ids_set = set(requested_ids)
        
        not_found_item_ids = list(requested_ids_set - valid_item_ids_set)
        
        condition_delete = and_(Cart_Item.id.in_(valid_item_ids))
        deleted_count = await cart_repository.hard_delete_cart_item(condition_delete, session)
        
        if deleted_count != len(valid_item_ids):
            logger.error(
                f"Deletion count mismatch: expected {len(valid_item_ids)}, "
                f"got {deleted_count}"
            )
            CartException.deletion_failed()

        return {
            'deleted_count': deleted_count,
            'valid_item_ids': valid_item_ids,
            'invalid_item_ids': not_found_item_ids,
            'not_found_item_ids': not_found_item_ids
        }
    
    
    def format_deletion_response(self, deletion_result: dict, requested_ids: List[str]) -> dict:
        deleted_count = deletion_result['deleted_count']
        not_found_count = len(deletion_result['not_found_item_ids'])

        response = {
            "deleted_items_count": deleted_count,
            "requested_items_count": len(requested_ids),
            "not_found_items_count": not_found_count,
        }

        if not_found_count > 0:
            response["not_found_item_ids"] = [
                str(item_id) for item_id in deletion_result['not_found_item_ids']
            ]

        return response