from fastapi import APIRouter, status, Depends, Query
from typing import Optional
from src.cache import CacheService, CacheKeys
from src.crud.color.services import ColorService
from src.dependencies import AccessTokenBearer
from src.schemas.color import ColorCreateModel, ColorFilterModel, ColorUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
import logging

color_admin_router = APIRouter(prefix="/color")
color_customer_router = APIRouter(prefix="/color")
color_staff_router = APIRouter(prefix="/color")

color_service = ColorService()
access_token_bearer = AccessTokenBearer()
cache_service = CacheService()
logger = logging.getLogger(__name__)

@color_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_color(color_data: ColorCreateModel,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    new_color_dict = await color_service.create_color_service(color_data, session)

    await cache_service.delete_pattern(CacheKeys.color_list_pattern())

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Màu mới vừa được thêm vào",
            "content": new_color_dict
        }
    )

@color_admin_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_all_color(search: Optional[str] = None,
                        skip: int = Query(0, ge=0),
                        limit: int = Query(10, ge=1, le=100),
                        token_details: dict = Depends(access_token_bearer),
                        session: AsyncSession = Depends(get_session)):
    filter_data = ColorFilterModel(search=search)

    should_cache = search is None
    cache_key = CacheKeys.color_list(skip, limit)

    if should_cache:
        cached_data = await cache_service.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Thông tin toàn bộ màu",
                    "content": cached_data
                }
            )

    logger.debug(f"Cache MISS: {cache_key}")

    colors_dict = await color_service.get_all_color(session, filter_data, skip, limit)

    if should_cache:
        await cache_service.set(cache_key, colors_dict, ttl=600)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin toàn bộ màu",
            "content": colors_dict
        }
    )

@color_admin_router.put('/{id}', dependencies=[Depends(admin_role_middleware)])
async def update_color(id: str, color_update: ColorUpdateModel,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    color_update_dict = await color_service.update_color_service(id, color_update, session)

    await cache_service.delete_pattern(CacheKeys.color_list_pattern())

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật màu sắc thành công",
            "content": color_update_dict
        }
    )

@color_admin_router.delete('/{id}', dependencies=[Depends(admin_role_middleware)])
async def delete_color(id: str, token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    color_deleted = await color_service.delete_color(id, session)

    await cache_service.delete_pattern(CacheKeys.color_list_pattern())

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa màu thành công",
            "content": color_deleted
        }
    )




