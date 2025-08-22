from fastapi import APIRouter, status, Depends
from src.crud.categories.services import CategoriesService
from src.dependencies import AccessTokenBearer
from src.schemas.categories import CategoriesCreateModel, CategoriesUpdateModel, CategoriesFilterModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from typing import Optional
import time

categories_admin_router = APIRouter(prefix="/categories")
categories_customer_router = APIRouter(prefix="/categories")
categories_common_router = APIRouter(prefix="/categories")

categories_service = CategoriesService()
access_token_bearer = AccessTokenBearer()


@categories_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_categories(categories_data: CategoriesCreateModel,
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    new_categories_dict = await categories_service.create_categories_service(categories_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Danh mục mới vừa được thêm vào",
            "content": new_categories_dict
        }
    )


@categories_admin_router.get('/all', dependencies=[Depends(admin_role_middleware)])
async def get_all_categories_admin(search: Optional[str] = None,
                                   parent_id: Optional[str] = None,
                                   type_size: Optional[str] = None,
                                   session: AsyncSession = Depends(get_session),
                                   skip: int = 0, limit: int = 5,
                                   token_details: dict = Depends(access_token_bearer)):
    filter_data = CategoriesFilterModel(
        search=search,
        parent_id=parent_id,
        type_size=type_size
    )

    categories = await categories_service.get_all_categories_service(filter_data, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các danh mục",
            "content": categories
        }
    )


@categories_customer_router.get('/all')
async def get_all_categories_customer(search: Optional[str] = None, session: AsyncSession = Depends(get_session),
                                      skip: int = 0, limit: int = 10):
    filter_data = CategoriesFilterModel(
        search=search
    )

    categories = await categories_service.get_all_categories_service(filter_data, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các danh mục",
            "content": categories
        }
    )


@categories_admin_router.get('/{id}', dependencies=[Depends(admin_role_middleware)])
async def get_detail_category(id: str,
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    categories_dict = await categories_service.get_detail_category_service(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh mục đang tìm kiếm",
            "content": categories_dict
        }
    )


@categories_admin_router.put('/{id}', dependencies=[Depends(admin_role_middleware)])
async def update_categories(id: str,
                            categories_update: CategoriesUpdateModel,
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    categories_update_dict = await categories_service.update_categories_service(id, categories_update, session)

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
    categories_delete = await categories_service.delete_categories_service(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa danh mục thành công",
            "content": categories_delete
        }
    )
