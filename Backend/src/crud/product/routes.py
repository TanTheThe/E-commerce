from fastapi import APIRouter, status, Depends, Query
from src.crud.product.services import ProductService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse

from src.errors.categories import CategoriesException
from src.schemas.product import ProductCreateModel, ProductUpdateModel, DeleteMultipleProductModel, ProductFilterModel
from src.dependencies import admin_role_middleware
from typing import Optional, List

product_admin_router = APIRouter(prefix="/product")
product_customer_router = APIRouter(prefix="/product")
product_common_router = APIRouter(prefix="/product")

product_service = ProductService()
access_token_bearer = AccessTokenBearer()


@product_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_product(product_data: ProductCreateModel,
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    product_dict = await product_service.create_product(product_data, session)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Sản phẩm mới vừa được thêm vào",
            "content": product_dict
        }
    )

@product_customer_router.get('/category')
async def get_all_products_customer(category_id: str,
                                    search: Optional[str] = None,
                                    category_ids: Optional[List[str]] = Query(default=[]),
                                    min_price: Optional[int] = None,
                                    max_price: Optional[int] = None,
                                    sort_by: Optional[str] = None,
                                    colors: Optional[List[str]] = Query(default=[]),
                                    sizes: Optional[List[str]] = Query(default=[]),
                                    rating: Optional[List[int]] = Query(default=[]),
                                    skip: int = 0, limit: int = 16,
                                    session: AsyncSession = Depends(get_session)):
    filter_data = ProductFilterModel(
        search=search,
        category_ids=category_ids,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        colors=colors,
        sizes=sizes,
        rating=rating
    )

    products = await product_service.get_all_products_customer_service(category_id, filter_data, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_customer_router.get('/popular/{parent_category_id}')
async def get_products_popular(parent_category_id: str, limit_per_category: int = 12, session: AsyncSession = Depends(get_session)):
    products = await product_service.get_products_popular_service(parent_category_id, session, limit_per_category)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_admin_router.get('/offer')
async def get_products_offer(categories_id: str, session: AsyncSession = Depends(get_session)):
    categories_list = [cat.strip() for cat in categories_id.split(',') if cat.strip()]
    if not categories_list:
        CategoriesException.empty_list()

    products = await product_service.get_all_product_for_offer(categories_list, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_customer_router.get('/latest')
async def get_products_latest(limit_per_category: int = 12, session: AsyncSession = Depends(get_session)):
    products = await product_service.get_latest_products_service(session, limit_per_category)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_customer_router.get('/top-discount')
async def get_products_top_discount(limit: int = 12, session: AsyncSession = Depends(get_session)):
    products = await product_service.get_top_discount_service(session, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_customer_router.get('/filter-info')
async def get_filters_info(category_id: str, session: AsyncSession = Depends(get_session)):
    filters = await product_service.get_filters_info_service(category_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các bộ lọc",
            "content": filters
        }
    )

@product_admin_router.get("/statistics/count-products", status_code=status.HTTP_200_OK,
                          dependencies=[Depends(admin_role_middleware)])
async def count_new_products(token_details: dict = Depends(access_token_bearer),
                             session: AsyncSession = Depends(get_session)):
    count_products = await product_service.count_all_products(session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thống kê số lượng",
            "content": {
                "count_products": count_products
            }
        }
    )


@product_admin_router.get('/all', dependencies=[Depends(admin_role_middleware)])
async def get_all_product_admin(search: Optional[str] = None,
                                category_ids: Optional[List[str]] = Query(default=[]),
                                min_price: Optional[int] = None,
                                max_price: Optional[int] = None,
                                sort_by: Optional[str] = None,
                                colors: Optional[List[str]] = None,
                                sizes: Optional[List[str]] = None,
                                rating: Optional[List[int]] = Query(None),
                                token_details: dict = Depends(access_token_bearer),
                                skip: int = 0, limit: int = 10,
                                session: AsyncSession = Depends(get_session)):
    filter_data = ProductFilterModel(
        search=search,
        category_ids=category_ids,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        colors=colors,
        sizes=sizes,
        rating=rating
    )

    product_list_dict = await product_service.get_all_product_admin_service(filter_data, session, skip, limit,
                                                                            include_status=True)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": product_list_dict
        }
    )


@product_customer_router.get('/{id}')
async def get_detail_product_customer(id: str, session: AsyncSession = Depends(get_session)):
    product_dict = await product_service.get_detail_product_customer_service(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết của sản phẩm",
            "content": product_dict
        }
    )


@product_admin_router.get('/{id}', dependencies=[Depends(admin_role_middleware)])
async def get_detail_product_admin(id: str,
                                   token_details: dict = Depends(access_token_bearer),
                                   session: AsyncSession = Depends(get_session)):
    product_dict = await product_service.get_detail_product_admin_service(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết của sản phẩm",
            "content": product_dict
        }
    )


@product_admin_router.get('/offer')
async def get_products_offer(categories_id: str, session: AsyncSession = Depends(get_session)):
    categories_list = [cat.strip() for cat in categories_id.split(',') if cat.strip()]
    if not categories_list:
        CategoriesException.empty_list()

    products = await product_service.get_all_product_for_offer(categories_list, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )


@product_admin_router.put('/{id}', dependencies=[Depends(admin_role_middleware)])
async def update_product(id: str, product_data: ProductUpdateModel,
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    product = await product_service.update_product(id, product_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật sản phẩm thành công",
            "content": product
        }
    )


@product_admin_router.delete('/{id}', dependencies=[Depends(admin_role_middleware)])
async def delete_product(id: str, token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    product = await product_service.delete_product(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa sản phẩm thành công",
            "content": product
        }
    )


@product_admin_router.post('/delete', dependencies=[Depends(admin_role_middleware)])
async def delete_multiple_product(data: DeleteMultipleProductModel, token_details: dict = Depends(access_token_bearer),
                                  session: AsyncSession = Depends(get_session)):
    product_ids = await product_service.delete_multiple_product(data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa sản phẩm thành công",
            "content": {
                "deleted_ids": product_ids
            }
        }
    )


