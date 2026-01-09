from enum import Enum
from fastapi import APIRouter, status, Depends, Query, Path
from src.cache import cache_service, CacheKeys
from src.crud.product.utils import invalidate_all_product_caches
from src.crud.special_offer.services.assign_offer_to_users import AssignOfferToUsersService
from src.crud.special_offer.services.create_special_offer import CreateSpecialOfferService
from src.crud.special_offer.services.delete_special_offer import DeleteSpecialOfferService
from src.crud.special_offer.services.get_all_special_offer import GetAllSpecialOfferService
from src.crud.special_offer.services.set_offers_to_product import SetOfferToProductService
from src.crud.special_offer.services.update_special_offer import UpdateSpecialOfferService
from src.crud.special_offer.utils import invalidate_offer_and_product_caches, invalidate_customer_offer_caches
from src.dependencies import AccessTokenBearer
from src.errors.special_offer import SpecialOfferException
from src.schemas.special_offer import SpecialOfferCreateModel, SpecialOfferUpdateModel, SpecialOfferFilterModel, \
    SetOfferToProduct, AssignOfferToUsers, OfferTypeEnum, OfferScopeEnum, QuantityStatusEnum, TimeStatusEnum
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware, customer_role_middleware
from typing import Optional
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

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

    await cache_service.delete_pattern(f"special_offer:admin:*")
    logger.info("Invalidated admin offer list cache after creating new offer")

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

    filter_dict = filter_data.model_dump()

    filter_dict = {
        k: (v.value if isinstance(v, Enum) else v)
        for k, v in filter_dict.items()
    }

    filter_hash = hashlib.md5(
        json.dumps(filter_dict, sort_keys=True, default=str).encode()
    ).hexdigest()[:12]

    cache_key = f"special_offer:admin:filter:{filter_hash}:skip:{skip}:limit:{limit}"

    cached_offers = await cache_service.get(cache_key)
    if cached_offers is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin các khuyến mãi",
                "content": cached_offers
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    special_offers = await get_all_special_offer_service.get_all_special_offer_admin(session, filter_data, skip=skip, limit=limit)

    await cache_service.set(cache_key, special_offers, ttl=300)

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

    # CRITICAL: Gắn offer vào products → giá products thay đổi
    # Phải invalidate TẤT CẢ product caches!
    await invalidate_all_product_caches()
    logger.info(f"Invalidated all product caches after setting offer to {result['updated_count']} products")

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

    search_hash = hashlib.md5(
        (search or "all").encode()
    ).hexdigest()[:8]

    cache_key = f"special_offer:customer:user:{user_id}:search:{search_hash}:skip:{skip}:limit:{limit}"

    cached_offers = await cache_service.get(cache_key)
    if cached_offers is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin các voucher",
                "content": cached_offers
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    special_offers = await get_all_special_offer_service.get_all_special_offer_customer(user_id, session, search, skip, limit)

    await cache_service.set(cache_key, special_offers, ttl=600)

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

    # Invalidate tất cả vì:
    # 1. Offer có thể đang được dùng bởi customers
    # 2. Offer có thể đang gắn vào products (giá thay đổi)
    await invalidate_offer_and_product_caches()

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

    # Invalidate cache của các users được assign offer
    # Giả sử result có key 'user_ids' hoặc 'assigned_user_ids'
    if 'user_ids' in result or 'assigned_user_ids' in result:
        user_ids = result.get('user_ids') or result.get('assigned_user_ids', [])
        if user_ids:
            await invalidate_customer_offer_caches(user_ids)

    await cache_service.delete_pattern(CacheKeys.special_offer_admin_list_pattern())

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

    # Invalidate tất cả vì:
    # 1. Customers có offer này cần refresh
    # 2. Products có offer này mất discount (giá thay đổi)
    await invalidate_offer_and_product_caches()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa voucher thành công",
            "content": special_offer_delete
        }
    )



