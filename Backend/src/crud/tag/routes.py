from fastapi import APIRouter, status, Depends
from typing import Optional

from pydantic import Field
from src.crud.tag.services.assign_tags_to_product import AssignTagsToProductService
from src.crud.tag.services.create_tag import CreateTagService
from src.crud.tag.services.get_all_tags import GetAllTagsService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.schemas.tag import TagAdminQueryParams, TagCreateModel, ProductTagAssignmentModel, TagQueryParams, TagUpdateModel, DeleteMultipleTagsModel

tag_admin_router = APIRouter(prefix="/tag")
tag_customer_router = APIRouter(prefix="/tag")
tag_staff_router = APIRouter(prefix="/tag")

create_tag_service = CreateTagService()
get_all_tags_service = GetAllTagsService()
assign_tags_to_product_service = AssignTagsToProductService()
access_token_bearer = AccessTokenBearer()

@tag_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_tag(tag_data: TagCreateModel,
                     token_details: dict = Depends(access_token_bearer),
                     session: AsyncSession = Depends(get_session)):
    tag_dict = await create_tag_service.create_tag_service(tag_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Tag mới vừa được thêm vào",
            "content": tag_dict
        }
    )

@tag_admin_router.get("/all", dependencies=[Depends(admin_role_middleware)])
async def get_all_tags_admin(params: TagAdminQueryParams = Depends(),
                             skip: int = Field(0, ge=0, description="Số bản ghi bỏ qua"),
                             limit: int = Field(10, ge=1, le=100, description="Số bản ghi trả về"),
                             token_details: dict = Depends(access_token_bearer),
                             session: AsyncSession = Depends(get_session)):
    tags = await get_all_tags_service.get_all_tags_admin(params, skip, limit, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách tags",
            "content": tags
        }
    )

@tag_admin_router.post("/assign-to-product", dependencies=[Depends(admin_role_middleware)])
async def assign_tags_to_product(assignment_data: ProductTagAssignmentModel,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    result = await assign_tags_to_product_service.assign_tags_to_product(assignment_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Gán tags cho sản phẩm thành công",
            "content": result
        }
    )

@tag_admin_router.put("/{id}", dependencies=[Depends(admin_role_middleware)])
async def update_tag(id: str, tag_data: TagUpdateModel,
                     token_details: dict = Depends(access_token_bearer),
                     session: AsyncSession = Depends(get_session)):
    tag = await tag_service.update_tag_service(id, tag_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật tag thành công",
            "content": tag
        }
    )


@tag_admin_router.delete("/{id}", dependencies=[Depends(admin_role_middleware)])
async def delete_tag(id: str, token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):
    result = await tag_service.delete_tag(id, session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa tag thành công",
            "content": result
        }
    )

@tag_admin_router.post("/delete", dependencies=[Depends(admin_role_middleware)])
async def delete_multiple_tags(data: DeleteMultipleTagsModel,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    result = await tag_service.delete_multiple_tags(data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Xóa {len(result)} tags thành công",
            "content": result
        }
    )

@tag_customer_router.get("/all")
async def get_all_tags_customer(params: TagQueryParams = Depends(),
                                skip: int = Field(0, ge=0, description="Số bản ghi bỏ qua"),
                                limit: int = Field(20, ge=1, le=50, description="Số bản ghi trả về"),
                                session: AsyncSession = Depends(get_session)):
    tags = await get_all_tags_service.get_all_tags_customer(params, skip, limit, session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách tags",
            "content": tags
        }
    )






