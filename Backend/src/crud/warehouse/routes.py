from fastapi import APIRouter, status, Depends
from typing import Optional
from src.crud.warehouse.services.assign_manager_to_warehouse import AssignManagerService
from src.crud.warehouse.services.assign_staff_to_warehouse import AssignStaffService
from src.crud.warehouse.services.create_warehouse import CreateWareHouseService
from src.crud.warehouse.services.get_warehouse_by_id import GetWarehouseByIDService
from src.crud.warehouse.services.remove_staff_from_warehouse import RemoveStaffService
from src.crud.warehouse.services.toggle_warehouse_status import ToggleWarehouseStatusService
from src.crud.warehouse.services.get_all_warehouses import GetAllWarehousesService
from src.crud.warehouse.services.set_default_warehouse import SetDefaultWarehouseService
from src.crud.warehouse.services.update_staff_role import UpdateStaffRoleService
from src.crud.warehouse.services.update_warehouse import UpdateWarehouseService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.schemas.user import StaffMultipleDeleteModel
from src.schemas.warehouse import WarehouseCreateModel, WarehouseUpdate, AssignManagerModel, UpdateStaffRoleModel, AssignMultipleStaffModel, AssignStaffItemModel

warehouse_admin_router = APIRouter(prefix="/warehouse")
warehouse_customer_router = APIRouter(prefix="/warehouse")
warehouse_staff_router = APIRouter(prefix="/warehouse")

create_warehouse_service = CreateWareHouseService()
get_all_warehouse_service = GetAllWarehousesService()
update_warehouse_service = UpdateWarehouseService()
set_default_warehouse_service = SetDefaultWarehouseService()
toggle_warehouse_status_service = ToggleWarehouseStatusService()
assign_manager_service = AssignManagerService()
assign_staff_service = AssignStaffService()
remove_staff_service = RemoveStaffService()
update_staff_role_service = UpdateStaffRoleService()
get_warehouse_by_id_service = GetWarehouseByIDService()
access_token_bearer = AccessTokenBearer()

@warehouse_admin_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_warehouse(warehouse_data: WarehouseCreateModel,
                           token_details: dict = Depends(access_token_bearer),
                           session: AsyncSession = Depends(get_session)):
    warehouse_dict = await create_warehouse_service.create_warehouse(warehouse_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Kho mới vừa được thêm vào",
            "content": warehouse_dict
        }
    )


@warehouse_admin_router.get("/all", dependencies=[Depends(admin_role_middleware)])
async def get_all_warehouses(search: Optional[str] = None,
                             is_active: Optional[bool] = None,
                             sort_by: Optional[str] = None,
                             skip: int = 0, limit: int = 10,
                             token_details: dict = Depends(access_token_bearer),
                             session: AsyncSession = Depends(get_session)):
    warehouses = await get_all_warehouse_service.get_all_warehouses(search, is_active, sort_by, skip, limit, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách các kho hiện tại",
            "content": warehouses
        }
    )


@warehouse_admin_router.get("/{warehouse_id}", dependencies=[Depends(admin_role_middleware)])
async def get_warehouse_by_id(warehouse_id: str,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    warehouse = await get_warehouse_by_id_service.get_warehouse_by_id(warehouse_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin kho",
            "content": warehouse
        }
    )


@warehouse_admin_router.post("/{warehouse_id}/set-default", dependencies=[Depends(admin_role_middleware)])
async def set_default_warehouse(warehouse_id: str,
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    await set_default_warehouse_service.set_default_warehouse(warehouse_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Gán mặc định cho kho thành công",
        }
    )


@warehouse_admin_router.post("/{warehouse_id}/assign-staff", dependencies=[Depends(admin_role_middleware)])
async def assign_staff_to_warehouse(warehouse_id: str,
                                      request_data: AssignStaffItemModel,
                                      token_details: dict = Depends(access_token_bearer),
                                      session: AsyncSession = Depends(get_session)):
    staff_after_assigned = await assign_staff_service.assign_staff_to_warehouse(warehouse_id, request_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Gán nhân viên kho thành công",
            "content": staff_after_assigned
        }
    )


@warehouse_admin_router.post("/{warehouse_id}/assign-staff/batch", dependencies=[Depends(admin_role_middleware)])
async def assign_multiple_staff_to_warehouse(warehouse_id: str,
                                             request_data: AssignMultipleStaffModel,
                                             token_details: dict = Depends(access_token_bearer),
                                             session: AsyncSession = Depends(get_session)):
    result = await assign_staff_service.assign_multiple_staff_to_warehouse(
        warehouse_id, request_data, session
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Gán {len(request_data.staff_list)} nhân viên kho thành công",
            "content": result
        }
    )


@warehouse_admin_router.put("/{warehouse_id}", dependencies=[Depends(admin_role_middleware)])
async def update_warehouse(warehouse_id: str, warehouse_update: WarehouseUpdate,
                           token_details: dict = Depends(access_token_bearer),
                           session: AsyncSession = Depends(get_session)):
    warehouse = await update_warehouse_service.update_warehouse(warehouse_id, warehouse_update, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật kho thành công",
            "content": warehouse
        }
    )


@warehouse_admin_router.put("/{warehouse_id}/change-status", dependencies=[Depends(admin_role_middleware)])
async def toggle_warehouse_status(warehouse_id: str,
                                  token_details: dict = Depends(access_token_bearer),
                                  session: AsyncSession = Depends(get_session)):
    await toggle_warehouse_status_service.toggle_warehouse_status(warehouse_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật trạng thái thành công",
        }
    )


@warehouse_admin_router.put("/{warehouse_id}/assign-manager", dependencies=[Depends(admin_role_middleware)])
async def assign_manager_to_warehouse(warehouse_id: str,
                                      request_data: AssignManagerModel,
                                      token_details: dict = Depends(access_token_bearer),
                                      session: AsyncSession = Depends(get_session)):
    await assign_manager_service.assign_manager_to_warehouse(warehouse_id, request_data.user_id,
                                                             request_data.new_role_for_old_manager,
                                                             session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Gán nhân viên làm quản lý kho thành công",
        }
    )


@warehouse_admin_router.put("/{warehouse_id}/staff/{user_id}/role", dependencies=[Depends(admin_role_middleware)])
async def update_staff_role(warehouse_id: str,
                            user_id: str,
                            request: UpdateStaffRoleModel,
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    staff_after_update_role = await update_staff_role_service.update_staff_role(warehouse_id, user_id, request, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Cập nhật role cho nhân viên thành công",
            "content": staff_after_update_role
        }
    )


@warehouse_admin_router.put("/{warehouse_id}/staff/batch", dependencies=[Depends(admin_role_middleware)])
async def remove_multiple_staff_from_warehouse(warehouse_id: str,
                                               request: StaffMultipleDeleteModel,
                                               token_details: dict = Depends(access_token_bearer),
                                               session: AsyncSession = Depends(get_session)):
    result = await remove_staff_service.remove_multiple_staff_from_warehouse(
        warehouse_id, request.user_ids, session
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Gỡ {result['total_removed']} nhân viên khỏi kho thành công",
            "content": result
        }
    )


@warehouse_admin_router.delete("/{warehouse_id}/staff/{user_id}", dependencies=[Depends(admin_role_middleware)])
async def remove_staff_from_warehouse(warehouse_id: str,
                                    user_id: str,
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    staff_after_removed = await remove_staff_service.remove_staff_from_warehouse(warehouse_id, user_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Gỡ nhân viên khỏi kho thành công",
            "content": staff_after_removed
        }
    )












