from fastapi import APIRouter, status, Depends
from typing import Optional
from src.crud.tag.services import TagService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.schemas.tag import TagCreateModel, ProductTagAssignmentModel, TagUpdateModel, DeleteMultipleTagsModel

tag_admin_router = APIRouter(prefix="/tag")
tag_customer_router = APIRouter(prefix="/tag")
tag_common_router = APIRouter(prefix="/tag")

tag_service = TagService()
access_token_bearer = AccessTokenBearer()

@tag_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_tag(tag_data: TagCreateModel,
                     token_details: dict = Depends(access_token_bearer),
                     session: AsyncSession = Depends(get_session)):
    tag_dict = await tag_service.create_tag_service(tag_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Tag mới vừa được thêm vào",
            "content": tag_dict
        }
    )

@tag_admin_router.get("/all", dependencies=[Depends(admin_role_middleware)])
async def get_all_tags_admin(search: Optional[str] = None,
                             is_active: Optional[bool] = None,
                             sort_by: Optional[str] = None,
                             skip: int = 0, limit: int = 10,
                             token_details: dict = Depends(access_token_bearer),
                             session: AsyncSession = Depends(get_session)):
    tags = await tag_service.get_all_tags_admin(search, is_active, sort_by, skip, limit, session)

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
    result = await tag_service.assign_tags_to_product(assignment_data, session)

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
async def get_all_tags_customer(search: Optional[str] = None,
                                skip: int = 0, limit: int = 20,
                                session: AsyncSession = Depends(get_session)):
    tags = await tag_service.get_all_tags_customer(search, skip, limit, session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách tags",
            "content": tags
        }
    )






