from fastapi import APIRouter, status, Depends
from typing import Optional
from src.crud.brand.services import BrandService
from src.dependencies import AccessTokenBearer
from src.schemas.brand import BrandCreateModel, BrandUpdateModel, DeleteMultipleBrandsModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware

brand_admin_router = APIRouter(prefix="/brand")
brand_customer_router = APIRouter(prefix="/brand")
brand_common_router = APIRouter(prefix="/brand")

brand_service = BrandService()
access_token_bearer = AccessTokenBearer()

@brand_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_brand(brand_data: BrandCreateModel,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    brand_dict = await brand_service.create_brand_service(brand_data, session)
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Thương hiệu mới vừa được thêm vào",
            "content": brand_dict
        }
    )

@brand_admin_router.get("/all", dependencies=[Depends(admin_role_middleware)])
async def get_all_brands_admin(search: Optional[str] = None,
                               is_active: Optional[bool] = None,
                               sort_by: Optional[str] = None,
                               skip: int = 0, 
                               limit: int = 10,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    brands = await brand_service.get_all_brands_admin(search, is_active, sort_by, skip, limit, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách thương hiệu",
            "content": brands
        }
    )
    
@brand_admin_router.put("/{id}", dependencies=[Depends(admin_role_middleware)])
async def update_brand(id: str, brand_data: BrandUpdateModel,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    brand = await brand_service.update_brand_service(id, brand_data, session)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật thương hiệu thành công",
            "content": brand
        }
    )

@brand_admin_router.delete("/{id}", dependencies=[Depends(admin_role_middleware)])
async def delete_brand(id: str, 
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    result = await brand_service.delete_brand(id, session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa thương hiệu thành công",
            "content": result
        }
    )

@brand_admin_router.post("/delete", dependencies=[Depends(admin_role_middleware)])
async def delete_multiple_brands(data: DeleteMultipleBrandsModel, 
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    result = await brand_service.delete_multiple_brands(data, session)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Xóa {len(result)} thương hiệu thành công",
            "content": result
        }
    )
    
@brand_customer_router.get("/all")
async def get_all_brands_customer(search: Optional[str] = None, 
                                  skip: int = 0, limit: int = 20,
                                  session: AsyncSession = Depends(get_session)):
    brands = await brand_service.get_all_brands_customer(search, skip, limit, session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách thương hiệu",
            "content": brands
        }
    )






