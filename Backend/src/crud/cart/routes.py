from fastapi import APIRouter, status, Depends
from src.crud.cart.services.create_cart import CreateCartService
from src.crud.cart.services.get_all_carts import GetAllCartsService
from src.crud.cart.services.get_cart_items_count import GetCartItemCountService
from src.crud.cart.services.remove_items import RemoveCartItemsService
from src.dependencies import AccessTokenBearer, customer_role_middleware
from src.schemas.cart import CartCreateModel, CartItemsDeleteModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse

cart_admin_router = APIRouter(prefix="/cart")
cart_customer_router = APIRouter(prefix="/cart")
cart_staff_router = APIRouter(prefix="/cart")

create_cart_service = CreateCartService()
get_all_carts_service = GetAllCartsService()
get_cart_item_count_service = GetCartItemCountService()
remove_cart_items_service = RemoveCartItemsService()
access_token_bearer = AccessTokenBearer()


@cart_customer_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(customer_role_middleware)])
async def create_cart_item(cart_data: CartCreateModel,
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    new_cart_dict = await create_cart_service.create_cart(user_id, cart_data, session)

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
    carts = await get_all_carts_service.get_all_cart(user_id, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin giỏ hàng",
            "content": carts
        }
    )

@cart_customer_router.get('/count')
async def get_cart_items_count(session: AsyncSession = Depends(get_session),
                               token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    count = await get_cart_item_count_service.get_cart_items_count(user_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin số lượng trong giỏ hàng",
            "content": count
        }
    )


@cart_customer_router.delete("/", dependencies=[Depends(customer_role_middleware)])
async def remove_cart_items(data: CartItemsDeleteModel,
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    carts = await remove_cart_items_service.remove_items_from_cart(user_id, data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin giỏ hàng sau khi xóa",
            "content": carts
        }
    )




