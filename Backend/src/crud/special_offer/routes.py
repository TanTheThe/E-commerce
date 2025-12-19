from fastapi import APIRouter, status, Depends, Query, Path

from src.crud.special_offer.services.assign_offer_to_users import AssignOfferToUsersService
from src.crud.special_offer.services.create_special_offer import CreateSpecialOfferService
from src.crud.special_offer.services.delete_special_offer import DeleteSpecialOfferService
from src.crud.special_offer.services.get_all_special_offer import GetAllSpecialOfferService
from src.crud.special_offer.services.set_offers_to_product import SetOfferToProductService
from src.crud.special_offer.services.update_special_offer import UpdateSpecialOfferService
from src.dependencies import AccessTokenBearer
from src.errors.special_offer import SpecialOfferException
from src.schemas.special_offer import SpecialOfferCreateModel, SpecialOfferUpdateModel, SpecialOfferFilterModel, \
    SetOfferToProduct, AssignOfferToUsers, OfferTypeEnum, OfferScopeEnum, QuantityStatusEnum, TimeStatusEnum
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware, customer_role_middleware
from typing import Optional

special_offer_admin_router = APIRouter(prefix="/special-offer")
special_offer_customer_router = APIRouter(prefix="/special-offer")
special_offer_staff_router = APIRouter(prefix="/special-offer")

create_special_offer_service = CreateSpecialOfferService()
get_all_special_offer_service = GetAllSpecialOfferService()
update_special_offer_service = UpdateSpecialOfferService()
set_offer_to_product_service = SetOfferToProductService()
assign_offer_to_users_service = AssignOfferToUsersService()
delete_special_offer_service = DeleteSpecialOfferService()
access_token_bearer = AccessTokenBearer()


@special_offer_admin_router.post("/", status_code=status.HTTP_201_CREATED,
                                 dependencies=[Depends(admin_role_middleware)])
async def create_special_offer(special_offer_data: SpecialOfferCreateModel,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    new_special_offer_dict = await create_special_offer_service.create_special_offer(special_offer_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Voucher mới vừa được thêm vào",
            "content": new_special_offer_dict
        }
    )


@special_offer_admin_router.get('/', dependencies=[Depends(admin_role_middleware)])
async def get_all_special_offer_admin(skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                      limit: int = Query(10, ge=1, le=100, description="Số bản ghi trả về (tối đa 100)"),
                                      search: Optional[str] = Query(None, max_length=255, description="Tìm kiếm theo code hoặc name"),
                                      type: Optional[OfferTypeEnum] = Query(None, description="Lọc theo loại giảm giá"),
                                      scope: Optional[OfferScopeEnum] = Query(None, description="Lọc theo phạm vi"),
                                      discount_min: Optional[int] = Query(None, ge=0, le=100, description="Giảm giá tối thiểu"),
                                      discount_max: Optional[int] = Query(None, ge=0, le=100, description="Giảm giá tối đa"),
                                      quantity_status: Optional[QuantityStatusEnum] = Query(None, description="Trạng thái số lượng"),
                                      time_status: Optional[TimeStatusEnum] = Query(None, description="Trạng thái thời gian"),
                                      session: AsyncSession = Depends(get_session),
                                      token_details: dict = Depends(access_token_bearer)):
    if discount_min is not None and discount_max is not None and discount_min > discount_max:
        SpecialOfferException.min_must_less_than_max()

    filter_data = SpecialOfferFilterModel(
        search=search,
        type=type,
        scope=scope,
        discount_min=discount_min,
        discount_max=discount_max,
        quantity_status=quantity_status,
        time_status=time_status
    )

    special_offers = await get_all_special_offer_service.get_all_special_offer_admin(session, filter_data, skip=skip, limit=limit)

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

    result = await set_offer_to_product_service.set_offer_to_product(data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đã gắn offer {result['special_offer_code']} vào {result['updated_count']} sản phẩm",
            "content": result
        }
    )


@special_offer_customer_router.get('/', dependencies=[Depends(customer_role_middleware)])
async def get_all_special_offer_customer(session: AsyncSession = Depends(get_session),
                                         token_details: dict = Depends(access_token_bearer),
                                         search: Optional[str] = Query(None, max_length=255, description="Tìm kiếm theo code hoặc name"),
                                         skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                         limit: int = Query(10, ge=1, le=100, description="Số bản ghi trả về (tối đa 100)")):

    user_id = token_details['user']['id']
    special_offers = await get_all_special_offer_service.get_all_special_offer_customer(user_id, session, search, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các voucher",
            "content": special_offers
        }
    )


@special_offer_admin_router.put('/{id}', dependencies=[Depends(admin_role_middleware)])
async def update_special_offer(id: str = Path(..., description="ID của special offer cần update"),
                               special_offer_update: SpecialOfferUpdateModel = ...,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    special_offer_update = await update_special_offer_service.update_special_offer(id, special_offer_update, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật voucher thành công",
            "content": special_offer_update
        }
    )

@special_offer_admin_router.post('/assign', dependencies=[Depends(admin_role_middleware)])
async def assign_offer_to_users(special_offer: AssignOfferToUsers,
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    result = await assign_offer_to_users_service.assign_offer_to_users(special_offer, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Gắn khuyến mãi cho khách hàng thành công",
            "content": result
        }
    )


@special_offer_admin_router.delete('/{id}', dependencies=[Depends(admin_role_middleware)])
async def delete_special_offer(id: str = Path(..., description="UUID của special offer cần xóa"),
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    special_offer_delete = await delete_special_offer_service.delete_special_offer(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa voucher thành công",
            "content": special_offer_delete
        }
    )



