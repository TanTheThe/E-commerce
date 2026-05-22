from fastapi import APIRouter, Path, status, Depends, Query
from src.cache import CacheKeys
from src.cache.cache_service import CacheService
from src.crud.product.services.create_product import CreateProductService
from src.crud.product.services.get_all_products_admin import GetAllProductsAdminService
from src.crud.product.services.get_all_products_customer import GetAllProductsCustomerService
from src.crud.product.services.get_all_products_for_offer import GetAllProductsOfferService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product.services.get_filters_info import GetFiltersInfoService
from src.crud.product.services.get_latest_products import GetLatestProductsService
from src.crud.product.services.get_product_variant_select_box import GetProductVariantSelectBoxService
from src.crud.product.services.get_products_popular import GetProductsPopularService
from src.crud.product.services.get_related_products import GetRelatedProductsService
from src.crud.product.services.get_top_discount import GetTopDiscountService
from src.crud.product.services.search_product import SearchProductService
from src.crud.product.services.services import ProductService
from src.crud.product.services.update_product.update_product import UpdateProductService
from src.crud.product.services.update_product_status import UpdateProductStatusService
from src.crud.product.utils import invalidate_all_product_caches
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.errors.categories import CategoriesException
from src.errors.product import ProductException
from src.schemas.product import ProductCreateModel, ProductUpdateModel, DeleteMultipleProductModel, ProductFilterModel, ProductStatusUpdateModel, BulkUpdateStatusModel, SortBy
from src.dependencies import admin_role_middleware
from typing import Optional, List
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

product_admin_router = APIRouter(prefix="/product")
product_customer_router = APIRouter(prefix="/product")
product_staff_router = APIRouter(prefix="/product")

product_service = ProductService()
create_product_service = CreateProductService()
get_all_products_customer_service = GetAllProductsCustomerService()
get_all_products_admin_service = GetAllProductsAdminService()
access_token_bearer = AccessTokenBearer()
search_product_service = SearchProductService()
get_detail_product_service = GetDetailProductService()
get_products_popular_service = GetProductsPopularService()
get_all_products_offer_service = GetAllProductsOfferService()
get_filters_info_service = GetFiltersInfoService()
get_latest_products_service = GetLatestProductsService()
get_related_products_service = GetRelatedProductsService()
get_top_discount_service = GetTopDiscountService()
get_product_variant_select_box_service = GetProductVariantSelectBoxService()
update_product_service = UpdateProductService()
update_product_status_service = UpdateProductStatusService()
cache_service = CacheService()


@product_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_product(product_data: ProductCreateModel,
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    product_dict = await create_product_service.create_product(product_data, session)

    await invalidate_all_product_caches()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Sản phẩm mới vừa được thêm vào",
            "content": product_dict
        }
    )


@product_customer_router.get('/category/{category_identifier}')
async def get_all_products_customer(category_identifier: str = Path(..., description="Category ID hoặc slug"),
                                    search: Optional[str] = Query(None, max_length=200),
                                    category_ids: Optional[List[str]] = Query(default=None, max_items=20),
                                    category_slugs: Optional[List[str]] = Query(default=None, max_items=20),
                                    min_price: Optional[int] = Query(None, ge=0),
                                    max_price: Optional[int] = Query(None, ge=0),
                                    sort_by: Optional[str] = Query(
                                        SortBy.newest,
                                        pattern="^(newest|oldest|price_asc|price_desc|name_asc|name_desc|best_seller|sale_desc|rating_desc)$"
                                    ),
                                    colors: Optional[List[str]] = Query(default=None, max_items=50),
                                    sizes: Optional[List[str]] = Query(default=None, max_items=20),
                                    rating: Optional[List[int]] = Query(default=None, ge=1, le=5, max_items=5),
                                    brand_id: Optional[str] = Query(None),
                                    material_ids: Optional[List[str]] = Query(default=None, max_items=20),
                                    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                    limit: int = Query(16, ge=1, le=100, description="Số bản ghi tối đa"),
                                    session: AsyncSession = Depends(get_session)):
    if not category_identifier or not category_identifier.strip():
        ProductException.category_identifier_must_not_be_empty()
    
    if min_price is not None and max_price is not None and min_price > max_price:
        ProductException.min_price_greater_than_max_price()
        
    filter_data = ProductFilterModel(
        search=search,
        category_ids=category_ids or [],
        category_slugs=category_slugs or [],
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        colors=colors or [],
        sizes=sizes or [],
        rating=rating or [],
        brand_id=brand_id,
        material_ids=material_ids or []
    )
    
    filter_dict = filter_data.model_dump()
    filter_dict = {k: (sorted(v) if isinstance(v, list) else v) for k, v in filter_dict.items()}
    filter_hash = hashlib.md5(json.dumps(filter_dict, sort_keys=True).encode()).hexdigest()[:12]
    
    category_identifier=category_identifier.strip()
    cache_key = CacheKeys.product_list_params(category_identifier, filter_hash, skip, limit)
    cached_products = await cache_service.get(cache_key)
    
    if cached_products is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin của các sản phẩm",
                "content": cached_products
            }
        )
        
    logger.debug(f"Cache MISS: {cache_key}")

    products = await get_all_products_customer_service.get_all_products_customer(category_identifier, filter_data, session, skip, limit)
    
    await cache_service.set(cache_key, products, ttl=600)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_customer_router.get('/popular/{parent_category_id}')
async def get_products_popular(parent_category_id: str = Path(
                                ..., min_length=1, max_length=255, description="Parent category ID"), 
                               limit_per_category: int = Query(
                                default=12, ge=1, le=50, description="Số sản phẩm tối đa cho mỗi category con"), 
                               session: AsyncSession = Depends(get_session)):
    cache_key = CacheKeys.product_popular(parent_category_id, limit_per_category)
    
    cached_products = await cache_service.get(cache_key)
    if cached_products is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin của các sản phẩm",
                "content": cached_products
            }
        )
        
    logger.debug(f"Cache MISS: {cache_key}")
        
    products = await get_products_popular_service.get_products_popular(parent_category_id, session, limit_per_category)
    
    await cache_service.set(cache_key, products, ttl=1800)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )

@product_customer_router.get('/search')
async def search_product(search: str = Query(
                            ..., 
                            min_length=1,
                            max_length=200,
                            description="Từ khóa tìm kiếm"
                        ),
                        skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                        limit: int = Query(10, ge=1, le=50, description="Số bản ghi tối đa"),
                        session: AsyncSession = Depends(get_session)):
    if not search or not search.strip():
        ProductException.search_must_not_be_empty()
        
    search_stripped = search.strip()
    if len(search_stripped) < 1:
        ProductException.search_too_short()
        
    products = await search_product_service.search_product(search, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin sau khi search",
            "content": products
        }
    )

@product_admin_router.get('/offer', dependencies=[Depends(admin_role_middleware)])
async def get_products_offer(categories_id: str = Query(..., description="Danh sách category IDs cách nhau bởi dấu phẩy"), 
                             session: AsyncSession = Depends(get_session)):
    categories_list = [cat.strip() for cat in categories_id.split(',') if cat.strip()]
    if not categories_list:
        CategoriesException.empty_list()
        
    if len(categories_list) > 20:
        CategoriesException.list_exceed_max_length(20)
        
    if len(categories_list) != len(set(categories_list)):
        CategoriesException.duplicate_ids_in_list()

    products = await get_all_products_offer_service.get_all_product_for_offer(categories_list, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )


@product_customer_router.get('/latest')
async def get_products_latest(limit_per_category: int = Query(default=12, ge=1, le=50, description="Số sản phẩm mới nhất cần lấy"), 
                              session: AsyncSession = Depends(get_session)):
    cache_key = CacheKeys.product_latest(limit_per_category)

    cached_products = await cache_service.get(cache_key)
    if cached_products is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin của các sản phẩm",
                "content": cached_products
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    products = await get_latest_products_service.get_latest_products(session, limit_per_category)

    await cache_service.set(cache_key, products, ttl=600)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )


@product_customer_router.get('/related')
async def get_products_related(product_id: str = Query(..., description="ID của sản phẩm cần tìm related products"), 
                               price_range: float = Query(default=0.4, ge=0.1, le=1.0, description="Khoảng giá tương đối (0.4 = ±40%)"),
                               limit_per_category: int = Query(default=12, ge=1, le=50, description="Số sản phẩm tối đa"),
                               session: AsyncSession = Depends(get_session)):
    cache_key = CacheKeys.product_related(product_id, price_range, limit_per_category)

    cached_products = await cache_service.get(cache_key)
    if cached_products is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin của các sản phẩm",
                "content": cached_products
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    products = await get_related_products_service.get_related_products(product_id, session, limit_per_category, price_range)

    await cache_service.set(cache_key, products, ttl=1200)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )


@product_customer_router.get('/top-discount')
async def get_products_top_discount(limit: int = Query(default=12, ge=1, le=50, description="Số sản phẩm giảm giá nhiều nhất"),
                                    session: AsyncSession = Depends(get_session)):
    cache_key = CacheKeys.product_top_discount(limit)

    cached_products = await cache_service.get(cache_key)
    if cached_products is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin của các sản phẩm",
                "content": cached_products
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    products = await get_top_discount_service.get_top_discount(session, limit)

    await cache_service.set(cache_key, products, ttl=1800)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )


@product_customer_router.get('/filter-info')
async def get_filters_info(category_id: str, session: AsyncSession = Depends(get_session)):
    cache_key = CacheKeys.product_filter_info(category_id)

    cached_filters = await cache_service.get(cache_key)
    if cached_filters is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin của các bộ lọc",
                "content": cached_filters
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    filters = await get_filters_info_service.get_filters_info(category_id, session)

    await cache_service.set(cache_key, filters, ttl=1800)

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
async def get_all_product_admin(search: Optional[str] = Query(None, max_length=200),
                                category_ids: Optional[List[str]] = Query(default=None, max_items=20),
                                category_slugs: Optional[List[str]] = Query(default=None, max_items=20),
                                min_price: Optional[int] = Query(None, ge=0),
                                max_price: Optional[int] = Query(None, ge=0),
                                sort_by: Optional[str] = Query(
                                    SortBy.newest,
                                    pattern="^(newest|oldest|price_asc|price_desc|name_asc|name_desc|best_seller|sale_desc|rating_desc)$"
                                ),
                                colors: Optional[List[str]] = Query(default=None, max_items=50),
                                sizes: Optional[List[str]] = Query(default=None, max_items=20),
                                rating: Optional[List[int]] = Query(default=None, ge=1, le=5, max_items=5),
                                brand_id: Optional[str] = Query(None),
                                material_ids: Optional[List[str]] = Query(default=None, max_items=20),
                                skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                limit: int = Query(16, ge=1, le=100, description="Số bản ghi tối đa"),
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    if min_price is not None and max_price is not None and min_price > max_price:
        ProductException.min_price_greater_than_max_price()
        
    filter_data = ProductFilterModel(
        search=search,
        category_ids=category_ids or [],
        category_slugs=category_slugs or [],
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        colors=colors or [],
        sizes=sizes or [],
        rating=rating or [],
        brand_id=brand_id,
        material_ids=material_ids or []
    )

    products = await get_all_products_admin_service.get_all_product_admin(filter_data, session, skip, limit,
                                                                                   include_status=True)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin của các sản phẩm",
            "content": products
        }
    )


@product_customer_router.get('/{identifier}')
async def get_detail_product_customer(identifier: str = Path(..., min_length=1, max_length=255, description="Product ID hoặc slug"), 
                                      session: AsyncSession = Depends(get_session)):
    if not identifier or not identifier.strip():
        ProductException.identifier_must_not_be_empty()

    identifier = identifier.strip()

    cache_key = CacheKeys.product_detail_customer(identifier)

    cached_product = await cache_service.get(cache_key)
    if cached_product is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin chi tiết của sản phẩm",
                "content": cached_product
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")
        
    product_dict = await get_detail_product_service.get_detail_product_customer(identifier.strip(), session)

    await cache_service.set(cache_key, product_dict, ttl=900)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết của sản phẩm",
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


@product_admin_router.get('/{identifier}', dependencies=[Depends(admin_role_middleware)])
async def get_detail_product_admin(identifier: str = Path(..., min_length=1, max_length=255, description="Product ID hoặc slug"),
                                   token_details: dict = Depends(access_token_bearer),
                                   session: AsyncSession = Depends(get_session)):
    if not identifier or not identifier.strip():
        ProductException.identifier_must_not_be_empty()
        
    product_dict = await get_detail_product_service.get_detail_product_admin(identifier.strip(), session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết của sản phẩm",
            "content": product_dict
        }
    )


@product_admin_router.get('/all/select-box', dependencies=[Depends(admin_role_middleware)])
async def get_products_selectbox(category_id: Optional[str] = None,
                                 supplier_id: Optional[str] = None,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    cache_key = CacheKeys.product_selectbox(category_id, supplier_id)

    cached_products = await cache_service.get(cache_key)
    if cached_products is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin các sản phẩm",
                "content": cached_products
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    product_dict = await get_product_variant_select_box_service.get_products_select_box(session, category_id, supplier_id)

    await cache_service.set(cache_key, product_dict, ttl=900)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các sản phẩm",
            "content": product_dict
        }
    )


@product_admin_router.get('/variants/all/select-box', dependencies=[Depends(admin_role_middleware)])
async def get_variants_selectbox(product_id: str,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    cache_key = CacheKeys.variants_selectbox(product_id)

    cached_variants = await cache_service.get(cache_key)
    if cached_variants is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin các biến thể",
                "content": cached_variants
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    variant_dict = await get_product_variant_select_box_service.get_variants_select_box(product_id, session)

    await cache_service.set(cache_key, variant_dict, ttl=900)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các biến thể",
            "content": variant_dict
        }
    )


@product_admin_router.put('/{id}', dependencies=[Depends(admin_role_middleware)])
async def update_product(id: str, product_data: ProductUpdateModel,
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    product = await update_product_service.update_product(id, product_data, session)

    await invalidate_all_product_caches()

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

    await invalidate_all_product_caches()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật trạng thái sản phẩm thành công",
            "content": {
                "product_id": id,
                "status": status_data.status.value
            }
        }
    )

@product_admin_router.post('/status/bulk', dependencies=[Depends(admin_role_middleware)])
async def bulk_update_product_status(bulk_data: BulkUpdateStatusModel,
                                     token_details: dict = Depends(access_token_bearer),
                                     session: AsyncSession = Depends(get_session)):
    await update_product_status_service.bulk_update_product_status(bulk_data, session)

    await invalidate_all_product_caches()
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật trạng thái các sản phẩm thành công",
            "content": {
                "product_ids": bulk_data.product_ids,
                "status": bulk_data.status.value
            }
        }
    )

@product_admin_router.delete('/{id}', dependencies=[Depends(admin_role_middleware)])
async def delete_product(id: str, token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    product = await product_service.delete_product(id, session)

    await invalidate_all_product_caches()

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

    await invalidate_all_product_caches()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa sản phẩm thành công",
            "content": {
                "deleted_ids": product_ids
            }
        }
    )


