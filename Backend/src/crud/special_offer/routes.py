from fastapi import APIRouter, status, Depends
from src.crud.special_offer.services import SpecialOfferService
from src.dependencies import AccessTokenBearer
from src.schemas.special_offer import SpecialOfferCreateModel, SpecialOfferUpdateModel, SpecialOfferFilterModel, \
    SetOfferToProduct
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware, customer_role_middleware
from typing import Optional

special_offer_admin_router = APIRouter(prefix="/special-offer")
special_offer_customer_router = APIRouter(prefix="/special-offer")
special_offer_common_router = APIRouter(prefix="/special-offer")

special_offer_service = SpecialOfferService()
access_token_bearer = AccessTokenBearer()


@special_offer_admin_router.post("/", status_code=status.HTTP_201_CREATED,
                                 dependencies=[Depends(admin_role_middleware)])
async def create_special_offer(special_offer_data: SpecialOfferCreateModel,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    new_special_offer_dict = await special_offer_service.create_special_offer_service(special_offer_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Voucher mới vừa được thêm vào",
            "content": new_special_offer_dict
        }
    )


@special_offer_admin_router.get('/', dependencies=[Depends(admin_role_middleware)])
async def get_all_special_offer_admin(skip: int = 0, limit: int = 10,
                                      search: Optional[str] = None,
                                      type: Optional[str] = None,
                                      scope: Optional[str] = None,
                                      discount_min: Optional[int] = None,
                                      discount_max: Optional[int] = None,
                                      quantity_status: Optional[str] = None,
                                      time_status: Optional[str] = None,
                                      session: AsyncSession = Depends(get_session),
                                      token_details: dict = Depends(access_token_bearer)):
    filter_data = SpecialOfferFilterModel(
        search=search,
        type=type,
        scope=scope,
        discount_min=discount_min,
        discount_max=discount_max,
        quantity_status=quantity_status,
        time_status=time_status
    )

    special_offers = await special_offer_service.get_all_special_offer_service(session, filter_data, skip=skip, limit=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các khuyến mãi",
            "content": special_offers
        }
    )


@special_offer_admin_router.post('/set-offer', dependencies=[Depends(admin_role_middleware)])
async def set_offer_to_product(data: SetOfferToProduct,
                               session: AsyncSession = Depends(get_session),
                               token_details: dict = Depends(access_token_bearer)):

    await special_offer_service.set_offer_to_product_service(data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Gắn offer thành công",
        }
    )


@special_offer_customer_router.get('/', dependencies=[Depends(customer_role_middleware)])
async def get_all_special_offer_customer(session: AsyncSession = Depends(get_session),
                                         token_details: dict = Depends(access_token_bearer)):
    special_offers = await special_offer_service.get_all_special_offer_service(session)

    filtered_special_offers = [
        {
            "code": special_offer.code,
            "name": special_offer.name,
            "discount": special_offer.discount,
            "condition": special_offer.condition,
            "type": special_offer.type,
            "start_time": str(special_offer.start_time),
            "end_time": str(special_offer.end_time),
        }
        for special_offer in special_offers
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các voucher",
            "content": filtered_special_offers
        }
    )


@special_offer_admin_router.put('/{id}', dependencies=[Depends(admin_role_middleware)])
async def update_special_offer(id: str,
                               special_offer_update: SpecialOfferUpdateModel,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    special_offer_update = await special_offer_service.update_special_offer_service(id, special_offer_update, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật voucher thành công",
            "content": special_offer_update
        }
    )


@special_offer_admin_router.delete('/{id}', dependencies=[Depends(admin_role_middleware)])
async def delete_categories(id: str, token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    special_offer_delete = await special_offer_service.delete_categories_service(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa voucher thành công",
            "content": special_offer_delete
        }
    )
