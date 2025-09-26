from fastapi import APIRouter, status, Depends, Query
from src.crud.product.services.create_product import CreateProductService
from src.crud.product.services.get_all_products import GetAllProductsService
from src.crud.product.services.get_all_products_for_offer import GetAllProductsOfferService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product.services.get_filters_info import GetFiltersInfoService
from src.crud.product.services.get_latest_products import GetLatestProductsService
from src.crud.product.services.get_products_popular import GetProductsPopularService
from src.crud.product.services.get_related_products import GetRelatedProductsService
from src.crud.product.services.get_top_discount import GetTopDiscountService
from src.crud.product.services.search_product import SearchProductService
from src.crud.product.services.services import ProductService
from src.crud.product.services.update_product import UpdateProductService
from src.crud.product.services.update_product_status import UpdateProductStatusService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.errors.categories import CategoriesException
from src.schemas.product import ProductCreateModel, ProductUpdateModel, DeleteMultipleProductModel, ProductFilterModel, ProductStatusUpdateModel, BulkUpdateStatusModel
from src.dependencies import admin_role_middleware
from typing import Optional, List

product_admin_router = APIRouter(prefix="/product")
product_customer_router = APIRouter(prefix="/product")
product_common_router = APIRouter(prefix="/product")

product_service = ProductService()
create_product_service = CreateProductService()
get_all_products_service = GetAllProductsService()
access_token_bearer = AccessTokenBearer()
search_product_service = SearchProductService()
get_detail_product_service = GetDetailProductService()
get_products_popular_service = GetProductsPopularService()
get_all_products_offer_service = GetAllProductsOfferService()
get_filters_info_service = GetFiltersInfoService()
get_latest_products_service = GetLatestProductsService()
get_related_products_service = GetRelatedProductsService()
get_top_discount_service = GetTopDiscountService()
update_product_service = UpdateProductService()
update_product_status_service = UpdateProductStatusService()


@product_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_product(product_data: ProductCreateModel,
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    product_dict = await create_product_service.create_product(product_data, session)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Sản phẩm mới vừa được thêm vào",
            "content": product_dict
        }
    )

@product_customer_router.get('/category')
async def get_all_products_customer(category_identifier: str,
                                    search: Optional[str] = None,
                                    category_ids: Optional[List[str]] = Query(default=[]),
                                    category_slugs: Optional[List[str]] = Query(default=[]),
                                    min_price: Optional[int] = None,
                                    max_price: Optional[int] = None,
                                    sort_by: Optional[str] = None,
                                    colors: Optional[List[str]] = Query(default=[]),
                                    sizes: Optional[List[str]] = Query(default=[]),
                                    rating: Optional[List[int]] = Query(default=[]),
                                    brand_id: Optional[str] = None,
                                    material_ids: Optional[List[str]] = Query(default=[]),
                                    skip: int = 0, limit: int = 16,
                                    session: AsyncSession = Depends(get_session)):
    filter_data = ProductFilterModel(
        search=search,
        category_ids=category_ids,
        category_slugs=category_slugs,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        colors=colors,
        sizes=sizes,
        rating=rating,
        brand_id=brand_id,
        material_ids=material_ids
    )

    products = await get_all_products_service.get_all_products_customer(category_identifier, filter_data, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_customer_router.get('/popular/{parent_category_id}')
async def get_products_popular(parent_category_id: str, limit_per_category: int = 12, session: AsyncSession = Depends(get_session)):
    products = await get_products_popular_service.get_products_popular(parent_category_id, session, limit_per_category)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_customer_router.get('/search')
async def search_product(search: str, session: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 10):
    products = await search_product_service.search_product(search, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin sau khi search",
            "content": products
        }
    )

@product_admin_router.get('/offer')
async def get_products_offer(categories_id: str, session: AsyncSession = Depends(get_session)):
    categories_list = [cat.strip() for cat in categories_id.split(',') if cat.strip()]
    if not categories_list:
        CategoriesException.empty_list()

    products = await get_all_products_offer_service.get_all_product_for_offer(categories_list, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_customer_router.get('/latest')
async def get_products_latest(limit_per_category: int = 12, session: AsyncSession = Depends(get_session)):
    products = await get_latest_products_service.get_latest_products(session, limit_per_category)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_customer_router.get('/related')
async def get_products_related(product_id: str, price_range: float = 0.4, limit_per_category: int = 12, session: AsyncSession = Depends(get_session)):
    products = await get_related_products_service.get_related_products(product_id, session, limit_per_category, price_range)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )


@product_customer_router.get('/top-discount')
async def get_products_top_discount(limit: int = 12, session: AsyncSession = Depends(get_session)):
    products = await get_top_discount_service.get_top_discount(session, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )


@product_customer_router.get('/filter-info')
async def get_filters_info(category_id: str, session: AsyncSession = Depends(get_session)):
    filters = await get_filters_info_service.get_filters_info(category_id, session)

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
                                brand_id: Optional[str] = None,
                                material_ids: Optional[List[str]] = Query(default=[]),
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
        rating=rating,
        brand_id=brand_id,
        material_ids=material_ids
    )

    product_list_dict = await get_all_products_service.get_all_product_admin(filter_data, session, skip, limit,
                                                                            include_status=True)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": product_list_dict
        }
    )


@product_customer_router.get('/{identifier}')
async def get_detail_product_customer(identifier: str, session: AsyncSession = Depends(get_session)):
    product_dict = await get_detail_product_service.get_detail_product_customer(identifier, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết của sản phẩm",
            "content": product_dict
        }
    )


@product_customer_router.get('/{product_identifier}/id')
async def get_product_id(product_identifier: str, session: AsyncSession = Depends(get_session)):
    product_id = await product_service.resolve_product_id(product_identifier, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin id của sản phẩm",
            "content": {
                "product_id": product_id
            }
        }
    )


@product_admin_router.get('/{id}', dependencies=[Depends(admin_role_middleware)])
async def get_detail_product_admin(id: str,
                                   token_details: dict = Depends(access_token_bearer),
                                   session: AsyncSession = Depends(get_session)):
    product_dict = await get_detail_product_service.get_detail_product_admin(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết của sản phẩm",
            "content": product_dict
        }
    )


@product_admin_router.put('/{id}', dependencies=[Depends(admin_role_middleware)])
async def update_product(id: str, product_data: ProductUpdateModel,
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    product = await update_product_service.update_product(id, product_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật sản phẩm thành công",
            "content": product
        }
    )

@product_admin_router.put('/{id}/status', dependencies=[Depends(admin_role_middleware)])
async def update_product_status(id: str, 
                                status_data: ProductStatusUpdateModel,
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    await update_product_status_service.update_product_status(id, status_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật trạng thái sản phẩm thành công",
        }
    )

@product_admin_router.post('/status/bulk', dependencies=[Depends(admin_role_middleware)])
async def bulk_update_product_status(bulk_data: BulkUpdateStatusModel,
                                     token_details: dict = Depends(access_token_bearer),
                                     session: AsyncSession = Depends(get_session)):
    await update_product_status_service.bulk_update_product_status(bulk_data, session)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật trạng thái các sản phẩm thành công",
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


