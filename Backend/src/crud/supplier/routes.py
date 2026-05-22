from typing import Optional
from fastapi import APIRouter, status, Depends, Query
from src.crud.supplier.services.create_supplier import CreateSupplierService
from src.crud.supplier.services.delete_supplier import DeleteSupplierService
from src.crud.supplier.services.get_all_suppliers import GetAllSuppliersService
from src.crud.supplier.services.get_detail_supplier import GetDetailSupplierService
from src.crud.supplier.services.update_supplier import UpdateSupplierService
from src.dependencies import AccessTokenBearer, admin_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.errors.supplier import SupplierException
from src.errors.user import UserException
from src.schemas.supplier import SupplierCreate, SupplierUpdate

suppliers_admin_router = APIRouter(prefix="/suppliers")
suppliers_staff_router = APIRouter(prefix="/suppliers")
suppliers_customer_router = APIRouter(prefix="/suppliers")


create_supplier_service = CreateSupplierService()
get_all_suppliers_service = GetAllSuppliersService()
get_detail_supplier_service = GetDetailSupplierService()
update_supplier_service = UpdateSupplierService()
delete_supplier_service = DeleteSupplierService()

access_token_bearer = AccessTokenBearer()


@suppliers_admin_router.post("/", dependencies=[Depends(admin_role_middleware)])
async def create_supplier(supplier_data: SupplierCreate,
                          token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):

    supplier = await create_supplier_service.create_supplier(supplier_data, session)
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Tạo thông tin nhà cung cấp thành công",
            "content": supplier
        }
    )


@suppliers_admin_router.get("/", dependencies=[Depends(admin_role_middleware)])
async def get_all_suppliers(is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái"),
                            search: Optional[str] = Query(None, description="Tìm kiếm theo tên, mã, người liên hệ", max_length=255),
                            skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                            limit: int = Query(10, ge=1, le=100, description="Số bản ghi trả về"),
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    suppliers = await get_all_suppliers_service.get_all_suppliers(session, search, is_active, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các nhà cung cấp",
            "content": suppliers
        }
    )


@suppliers_admin_router.get("/{supplier_id}", dependencies=[Depends(admin_role_middleware)])
async def get_detail_supplier(supplier_id: str,
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    supplier = await get_detail_supplier_service.get_supplier_by_id(session, supplier_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết của nhà cung cấp",
            "content": supplier
        }
    )


@suppliers_admin_router.put("/{supplier_id}", dependencies=[Depends(admin_role_middleware)])
async def update_supplier(supplier_id: str, supplier_data: SupplierUpdate,
                          token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):
    result = await update_supplier_service.update_supplier(supplier_id, supplier_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật thông tin nhà cung cấp thành công",
            "content": result
        }
    )


@suppliers_admin_router.delete("/{supplier_id}", dependencies=[Depends(admin_role_middleware)])
async def delete_supplier(supplier_id: str,
                          force: bool = Query(False, description="Force delete (bỏ qua một số validation)"),
                          permanent: bool = Query(False, description="Xóa vĩnh viễn thay vì soft delete"),
                          token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):
    if permanent:
        role = token_details.get('role')
        if role != 'admin':
            SupplierException.only_admin_can_permanent_delete()
            
    result = await delete_supplier_service.delete_supplier(
        supplier_id=supplier_id,
        session=session,
        force=force,
        permanent=permanent
    )
    
    message = "Xóa nhà cung cấp vĩnh viễn thành công" if permanent else "Vô hiệu hóa nhà cung cấp thành công"

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message,
            "content": result
        }
    )














