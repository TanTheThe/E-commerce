from fastapi import APIRouter, status, Depends
from typing import Optional
from src.crud.color.services import ColorService
from src.dependencies import AccessTokenBearer
from src.schemas.color import ColorCreateModel, ColorFilterModel, ColorUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware

color_admin_router = APIRouter(prefix="/color")
color_customer_router = APIRouter(prefix="/color")
color_common_router = APIRouter(prefix="/color")

color_service = ColorService()
access_token_bearer = AccessTokenBearer()

@color_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_color(color_data: ColorCreateModel,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    new_color_dict = await color_service.create_color_service(color_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Màu mới vừa được thêm vào",
            "content": new_color_dict
        }
    )

@color_admin_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_all_color(search: Optional[str] = None,
                        skip: int = 0, limit: int = 10,
                        token_details: dict = Depends(access_token_bearer),
                        session: AsyncSession = Depends(get_session)):
    filter_data = ColorFilterModel(search=search)
    colors_dict = await color_service.get_all_color(session, filter_data, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin toàn bộ màu",
            "content": colors_dict
        }
    )

@color_admin_router.put('/{id}', dependencies=[Depends(admin_role_middleware)])
async def update_color(id: str,
                       color_update: ColorUpdateModel,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    color_update_dict = await color_service.update_color_service(id, color_update, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật màu sắc thành công",
            "content": color_update_dict
        }
    )

@color_admin_router.delete('/{id}', dependencies=[Depends(admin_role_middleware)])
async def delete_color(id: str,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    color_deleted = await color_service.delete_color(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa màu thành công",
            "content": color_deleted
        }
    )




