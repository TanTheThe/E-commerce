from datetime import datetime

from fastapi import APIRouter, status, Depends, Query, Path, Body

from src.crud.user.services.delete_user import DeleteUserService
from src.crud.user.services.get_all_users import GetAllUsersService
from src.crud.user.services.get_for_offer import GetAllCustomerForOfferService
from src.crud.user.services.get_profile_customer import GetProfileCustomerService
from src.crud.user.services.get_staffs import GetStaffsService
from src.crud.user.services.update_profile_service import UpdateProfileService
from src.dependencies import AccessTokenBearer
from src.errors.user import UserException
from src.schemas.stock import WarehouseRole
from src.schemas.user import UserUpdateModel, UserDeleteModel, FilterUserInputModel, UserStatus, UserRole
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from src.crud.user.services import UserService
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware, customer_role_middleware
from typing import Optional

user_service = UserService()
get_all_users_service = GetAllUsersService()
get_staffs_service = GetStaffsService()
get_all_customer_for_offer_service = GetAllCustomerForOfferService()
update_profile_service = UpdateProfileService()
get_profile_customer_service = GetProfileCustomerService()
delete_user_service = DeleteUserService()
access_token_bearer = AccessTokenBearer()

user_admin_router = APIRouter(prefix="/user")
user_customer_router = APIRouter(prefix="/user")
user_staff_router = APIRouter(prefix="/user")


@user_admin_router.get('/all-customers', dependencies=[Depends(admin_role_middleware)])
async def get_all_customers(search: Optional[str] = Query(None, max_length=100, description="Tìm kiếm theo tên hoặc email"),
                            email: Optional[str] = Query(None, max_length=255),
                            phone: Optional[str] = Query(None, max_length=20),
                            customer_status: Optional[UserStatus] = None,
                            is_verified: Optional[bool] = None,
                            sort_by_created_at: Optional[str] = Query(None, regex="^(newest|oldest)$"),
                            skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                            limit: int = Query(10, ge=1, le=100, description="Số bản ghi tối đa"),
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    filter_data = FilterUserInputModel(
        search=search,
        email=email,
        phone=phone,
        status=customer_status,
        sort_by_created_at=sort_by_created_at,
        is_verified=is_verified,
        warehouse_role=None,
        warehouse_code=None
    )

    if skip < 0 or limit < 1 or limit > 100:
        raise ValueError("Invalid pagination parameters")

    filtered_users = await get_all_users_service.get_all_users(filter_data, UserRole.CUSTOMER, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin người dùng",
            "content": filtered_users
        }
    )


@user_admin_router.get('/all-staffs', dependencies=[Depends(admin_role_middleware)])
async def get_all_staffs(search: Optional[str] = Query(None, max_length=100, description="Tìm kiếm theo tên hoặc email"),
                         email: Optional[str] = Query(None, max_length=255),
                         phone: Optional[str] = Query(None, max_length=20),
                         staff_status: Optional[UserStatus] = None,
                         is_verified: Optional[bool] = None,
                         sort_by_created_at: Optional[str] = Query(None, regex="^(newest|oldest)$"),
                         warehouse_code: Optional[str] = Query(None, max_length=50, description="Mã kho"),
                         warehouse_role: Optional[WarehouseRole] = Query(None, description="Vai trò trong kho"),
                         skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                         limit: int = Query(10, ge=1, le=100, description="Số bản ghi tối đa"),
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    filter_data = FilterUserInputModel(
        search=search,
        email=email,
        phone=phone,
        status=staff_status,
        sort_by_created_at=sort_by_created_at,
        is_verified=is_verified,
        warehouse_role=warehouse_role,
        warehouse_code=warehouse_code,
    )

    filtered_users = await user_service.get_all_users_service(filter_data, UserRole.STAFF, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin người dùng",
            "content": filtered_users
        }
    )


@user_admin_router.get('/available-staffs', dependencies=[Depends(admin_role_middleware)])
async def get_available_staffs(skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                               limit: int = Query(10, ge=1, le=100, description="Số bản ghi tối đa"),
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    available_staffs = await get_staffs_service.get_available_staffs_service(session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách nhân viên chưa phân kho",
            "content": available_staffs
        }
    )


@user_admin_router.get('/warehouse/{warehouse_id}/staffs', dependencies=[Depends(admin_role_middleware)])
async def get_staffs_by_warehouse(warehouse_id: str = Path(..., description="UUID của warehouse"),
                                  skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                  limit: int = Query(10, ge=1, le=100, description="Số bản ghi tối đa"),
                                  token_details: dict = Depends(access_token_bearer),
                                  session: AsyncSession = Depends(get_session)):
    staffs = await get_staffs_service.get_staffs_by_warehouse_service(warehouse_id, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách nhân viên trong kho",
            "content": staffs
        }
    )


@user_admin_router.get('/available-for-offer/{offer_id}', dependencies=[Depends(admin_role_middleware)])
async def get_all_customer_for_offer(offer_id: str = Path(..., description="UUID của special offer"),
                                     search: Optional[str] = Query(None, max_length=100, description="Tìm kiếm theo tên hoặc email"),
                                     skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                     limit: int = Query(10, ge=1, le=100, description="Số bản ghi tối đa"),
                                     token_details: dict = Depends(access_token_bearer),
                                     session: AsyncSession = Depends(get_session)):
    if search:
        search = search.strip()
        if len(search) < 2:
            UserException.search_must_have_at_least_2_characters()

    filtered_users = await get_all_customer_for_offer_service.get_all_customer_for_offer(offer_id, search, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin người dùng",
            "content": filtered_users
        }
    )


# @user_admin_router.get('/{id}', dependencies=[Depends(admin_role_middleware)])
# async def get_detail_by_admin(id: str, token_details: dict = Depends(access_token_bearer),
#                               session: AsyncSession = Depends(get_session)):
#     filtered_user = await user_service.get_detail_admin_service(id, session)
#
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={
#             "message": "Thông tin người dùng",
#             "content": filtered_user
#         }
#     )


@user_admin_router.get('')
async def get_profile_admin(token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    role = token_details.get('role')

    if not user_id:
        UserException.token_invalid()

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    filtered_user = await user_service.get_profile_admin_staff_service(user_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Lấy thông tin thành công",
            "content": filtered_user
        }
    )


@user_admin_router.put('', dependencies=[Depends(admin_role_middleware)])
async def update_profile_admin(user_update_data: UserUpdateModel = Body(..., description="Dữ liệu cập nhật profile"),
                               session: AsyncSession = Depends(get_session),
                               token_details: dict = Depends(access_token_bearer)):
    user_id = token_details.get('user', {}).get('id')

    if not user_id:
        UserException.token_invalid()

    updated_user = await update_profile_service.update_profile(user_id, user_update_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật thông tin người dùng thành công",
            "content": {
                "id": str(updated_user.id),
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "phone": updated_user.phone,
                "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
            }
        }
    )


@user_customer_router.put('/', dependencies=[Depends(customer_role_middleware)])
async def update_profile_customer(user_update_data: UserUpdateModel = Body(..., description="Dữ liệu cập nhật profile"),
                                  session: AsyncSession = Depends(get_session),
                                  token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    if not user_id:
        UserException.token_invalid()

    updated_user = await update_profile_service.update_profile(user_id, user_update_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật thông tin người dùng thành công",
            "content": {
                "id": str(updated_user.id),
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "phone": updated_user.phone,
                "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
            }
        }
    )


@user_customer_router.get('/', dependencies=[Depends(customer_role_middleware)])
async def get_profile_customer(token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    if not user_id:
        UserException.token_invalid()

    filtered_user = await get_profile_customer_service.get_profile_customer(user_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin người dùng",
            "content": filtered_user
        }
    )


@user_admin_router.delete('/{user_id}', dependencies=[Depends(admin_role_middleware)])
async def delete_user(user_id: str = Path(..., description="UUID của user cần xóa"),
                      token_details: dict = Depends(access_token_bearer),
                      session: AsyncSession = Depends(get_session)):
    admin_id = token_details['user']['id']
    if not admin_id:
        UserException.token_invalid()

    if user_id == admin_id:
        UserException.cant_delete_oneself()

    deleted_user_id = await delete_user_service.delete_user(user_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa người dùng thành công",
            "content": {
                "id": deleted_user_id,
                "deleted_at": datetime.now().isoformat()
            }
        }
    )


@user_admin_router.post('/delete-batch', dependencies=[Depends(admin_role_middleware)])
async def delete_multiple_users(data: UserDeleteModel = Body(..., description="Danh sách user IDs cần xóa"),
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    admin_id = token_details['user']['id']

    if not admin_id:
        UserException.token_invalid()

    if admin_id in data.user_ids:
        UserException.cant_delete_oneself()

    result = await delete_user_service.delete_multiple_user(data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Xóa thành công {result['deleted_count']}/{result['requested_count']} người dùng",
            "content": result
        }
    )


@user_admin_router.put('/{id}/change-staff-status', dependencies=[Depends(admin_role_middleware)])
async def change_status_staff(id: str, token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    user_block = await user_service.change_status_user(id, UserRole.STAFF, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Chặn người dùng thành công",
            "content": user_block
        }
    )


@user_admin_router.put('/{id}/change-customer-status', dependencies=[Depends(admin_role_middleware)])
async def change_status_customer(id: str, token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    user_block = await user_service.change_status_user(id, UserRole.CUSTOMER, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Chặn người dùng thành công",
            "content": user_block
        }
    )
