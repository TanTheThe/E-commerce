from fastapi import APIRouter, status, Depends, Query
from src.cache import cache_service, CacheKeys
from src.crud.categories.services.create_category import CreateCategoryService
from src.crud.categories.services.get_all_categories import GetAllCategoriesService
from src.crud.categories.services.remaining_services import RemainingCategoriesService
from src.crud.categories.services.update_categories import UpdateCategoryService
from src.dependencies import AccessTokenBearer
from src.schemas.categories import CategoriesCreateModel, CategoriesFilterModel, CategoryUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from typing import Optional
import logging

logger = logging.getLogger(__name__)

categories_admin_router = APIRouter(prefix="/categories")
categories_customer_router = APIRouter(prefix="/categories")
categories_staff_router = APIRouter(prefix="/categories")

create_category_service = CreateCategoryService()
get_all_categories_service = GetAllCategoriesService()
update_category_service = UpdateCategoryService()
remaining_categories_service = RemainingCategoriesService()
access_token_bearer = AccessTokenBearer()


@categories_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_categories(categories_data: CategoriesCreateModel,
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    new_categories_dict = await create_category_service.create_category(categories_data, session)

    await cache_service.delete(CacheKeys.category_tree())
    await cache_service.delete_pattern("category:list:customer:*")

    if categories_data.parent_id:
        await cache_service.delete(CacheKeys.category_detail(str(categories_data.parent_id)))

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Danh mục mới vừa được thêm vào",
            "content": new_categories_dict
        }
    )


@categories_admin_router.get('/all', dependencies=[Depends(admin_role_middleware)])
async def get_all_categories_admin(search: Optional[str] = Query(None, description="Tìm kiếm theo tên", max_length=255),
                                   parent_id: Optional[str] = Query(None, description="Lọc theo ID danh mục cha"),
                                   type_size: Optional[str] = Query(None, description="Lọc theo loại size", max_length=50),
                                   skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                   limit: int = Query(5, ge=1, le=100, description="Số bản ghi mỗi trang"),
                                   session: AsyncSession = Depends(get_session),
                                   token_details: dict = Depends(access_token_bearer)):
    filter_data = CategoriesFilterModel(
        search=search,
        parent_id=parent_id,
        type_size=type_size
    )

    categories = await get_all_categories_service.get_all_categories(filter_data, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các danh mục",
            "content": categories
        }
    )


@categories_customer_router.get('/all')
async def get_all_categories_customer(search: Optional[str] = Query(None, description="Tìm kiếm theo tên", max_length=255),
                                      skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                      limit: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
                                      session: AsyncSession = Depends(get_session)):
    filter_data = CategoriesFilterModel(
        search=search,
        parent_id=None,
        type_size=None
    )

    should_cache = search is None and skip == 0 and limit == 10
    cache_key = f"category:list:customer:skip:{skip}:limit:{limit}"

    if should_cache:
        cached_data = await cache_service.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Thông tin các danh mục",
                    "content": cached_data
                }
            )

    categories = await get_all_categories_service.get_all_categories(filter_data, session, skip, limit)

    if should_cache:
        await cache_service.set(cache_key, categories, ttl=600)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các danh mục",
            "content": categories
        }
    )


@categories_customer_router.get('/{category_identifier}/id')
async def get_category_id(category_identifier: str, session: AsyncSession = Depends(get_session)):
    cache_key = f"category:resolve:{category_identifier}"
    cached_id = await cache_service.get(cache_key)

    if cached_id is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin id của danh mục",
                "content": {
                    "category_id": cached_id
                }
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    category_id = await remaining_categories_service.resolve_category_id(category_identifier, session)

    if category_id:
        await cache_service.set(cache_key, category_id, ttl=3600)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin id của danh mục",
            "content": {
                "category_id": category_id
            }
        }
    )


@categories_admin_router.get('/{id}', dependencies=[Depends(admin_role_middleware)])
async def get_detail_category(id: str,
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    cache_key = f"category:detail:{id}"
    cached_data = await cache_service.get(cache_key)

    if cached_data is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Danh mục đang tìm kiếm",
                "content": cached_data
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    categories_dict = await remaining_categories_service.get_detail_category_service(id, session)

    await cache_service.set(cache_key, categories_dict, ttl=1800)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh mục đang tìm kiếm",
            "content": categories_dict
        }
    )


@categories_admin_router.get('/all/select-box')
async def get_categories_select_box(session: AsyncSession = Depends(get_session),
                                    token_details: dict = Depends(access_token_bearer)):
    cache_key = "category:tree:all"
    cached_data = await cache_service.get(cache_key)

    if cached_data is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin của các sản phẩm",
                "content": cached_data
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    categories = await remaining_categories_service.get_categories_select_box_service(session)

    await cache_service.set(cache_key, categories, ttl=3600)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các danh mục",
            "content": categories
        }
    )


@categories_admin_router.put('/{id}', dependencies=[Depends(admin_role_middleware)])
async def update_categories(id: str, categories_update: CategoryUpdateModel,
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    categories_update_dict = await update_category_service.update_category(id, categories_update, session)

    await cache_service.delete(CacheKeys.category_tree())  # select-box
    await cache_service.delete(CacheKeys.category_detail(id))  # detail cache
    await cache_service.delete_pattern("category:list:customer:*")  # customer list
    await cache_service.delete_pattern(f"category:resolve:*")  # slug/id mapping

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật danh mục thành công",
            "content": categories_update_dict
        }
    )


@categories_admin_router.delete('/{id}', dependencies=[Depends(admin_role_middleware)])
async def delete_categories(id: str, token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    categories_delete = await remaining_categories_service.delete_categories_service(id, session)

    await cache_service.delete(CacheKeys.category_tree())  # select-box
    await cache_service.delete(CacheKeys.category_detail(id))  # detail
    await cache_service.delete_pattern("category:list:customer:*")  # lists
    await cache_service.delete_pattern(f"category:resolve:*")  # mappings

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa danh mục thành công",
            "content": categories_delete
        }
    )
