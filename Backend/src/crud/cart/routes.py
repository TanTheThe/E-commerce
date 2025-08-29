from typing import List

from fastapi import APIRouter, status, Depends
from src.crud.cart.services import CartService
from src.dependencies import AccessTokenBearer, customer_role_middleware
from src.schemas.cart import CartCreateModel, CartItemsDeleteModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse

cart_admin_router = APIRouter(prefix="/cart")
cart_customer_router = APIRouter(prefix="/cart")
cart_common_router = APIRouter(prefix="/cart")

cart_service = CartService()
access_token_bearer = AccessTokenBearer()


@cart_customer_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(customer_role_middleware)])
async def create_cart_item(cart_data: CartCreateModel,
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    new_cart_dict = await cart_service.create_cart_service(user_id, cart_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Vừa thêm sản phẩm vào giỏ hàng",
            "content": new_cart_dict
        }
    )


@cart_customer_router.get('/')
async def get_all_cart(session: AsyncSession = Depends(get_session),
                       token_details: dict = Depends(access_token_bearer),
                       skip: int = 0, limit: int = 10):
    user_id = token_details['user']['id']
    carts = await cart_service.get_all_cart_service(user_id, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin giỏ hàng",
            "content": carts
        }
    )


@cart_customer_router.delete("/", dependencies=[Depends(customer_role_middleware)])
async def remove_cart_items(data: CartItemsDeleteModel,
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    carts = await cart_service.remove_items_from_cart(user_id, data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin giỏ hàng sau khi xóa",
            "content": carts
        }
    )




