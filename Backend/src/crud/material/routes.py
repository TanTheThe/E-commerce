from fastapi import APIRouter, status, Depends
from typing import Optional
from src.crud.material.services import MaterialService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.schemas.material import MaterialCreateModel, ProductMaterialAssignmentModel, MaterialUpdateModel, \
    DeleteMultipleMaterialsModel

material_admin_router = APIRouter(prefix="/material")
material_customer_router = APIRouter(prefix="/material")
material_common_router = APIRouter(prefix="/material")

material_service = MaterialService()
access_token_bearer = AccessTokenBearer()

@material_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_material(material_data: MaterialCreateModel,
                          token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):
    material_dict = await material_service.create_material_service(material_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Chất liệu mới vừa được thêm vào",
            "content": material_dict
        }
    )

@material_admin_router.get("/all", dependencies=[Depends(admin_role_middleware)])
async def get_all_materials_admin(search: Optional[str] = None,
                                  is_active: Optional[bool] = None,
                                  sort_by: Optional[str] = None,
                                  skip: int = 0, limit: int = 10,
                                  token_details: dict = Depends(access_token_bearer),
                                  session: AsyncSession = Depends(get_session)):
    materials = await material_service.get_all_materials_admin(search, is_active, sort_by, skip, limit, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách chất liệu",
            "content": materials
        }
    )

@material_admin_router.post("/assign-to-product", dependencies=[Depends(admin_role_middleware)])
async def assign_materials_to_product(assignment_data: ProductMaterialAssignmentModel,
                                      token_details: dict = Depends(access_token_bearer),
                                      session: AsyncSession = Depends(get_session)):
    result = await material_service.assign_materials_to_product(assignment_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Gán chất liệu cho sản phẩm thành công",
            "content": result
        }
    )

@material_admin_router.put("/{id}", dependencies=[Depends(admin_role_middleware)])
async def update_material(id: str, material_data: MaterialUpdateModel,
                          token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):
    material = await material_service.update_material_service(id, material_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật chất liệu thành công",
            "content": material
        }
    )


@material_admin_router.delete("/{id}", dependencies=[Depends(admin_role_middleware)])
async def delete_material(id: str, token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):
    result = await material_service.delete_material(id, session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa chất liệu thành công",
            "content": result
        }
    )

@material_admin_router.post("/delete", dependencies=[Depends(admin_role_middleware)])
async def delete_multiple_materials(data: DeleteMultipleMaterialsModel,
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    result = await material_service.delete_multiple_materials(data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Xóa {len(result)} chất liệu thành công",
            "content": result
        }
    )

@material_customer_router.get("/all")
async def get_all_materials_customer(search: Optional[str] = None,
                                     skip: int = 0, limit: int = 20,
                                     session: AsyncSession = Depends(get_session)):
    tags = await material_service.get_all_materials_customer(search, skip, limit, session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách chất liệu",
            "content": tags
        }
    )






