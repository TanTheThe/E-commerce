from fastapi import APIRouter, status, Depends
from src.dependencies import AccessTokenBearer, staff_role_middleware
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
access_token_bearer = AccessTokenBearer()

user_admin_router = APIRouter(prefix="/user")
user_customer_router = APIRouter(prefix="/user")
user_staff_router = APIRouter(prefix="/user")


@user_admin_router.get('/all-customers', dependencies=[Depends(admin_role_middleware)])
async def get_all_customers(search: Optional[str] = None,
                            email: Optional[str] = None,
                            phone: Optional[str] = None,
                            customer_status: Optional[UserStatus] = None,
                            is_verified: Optional[bool] = None,
                            sort_by_created_at: Optional[str] = None,
                            token_details: dict = Depends(access_token_bearer),
                            skip: int = 0, limit: int = 10,
                            session: AsyncSession = Depends(get_session)):
    filter_data = FilterUserInputModel(
        search=search,
        email=email,
        phone=phone,
        status=customer_status,
        sort_by_created_at=sort_by_created_at,
        is_verified=is_verified,
    )

    filtered_users = await user_service.get_all_users_service(filter_data, UserRole.CUSTOMER, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin người dùng",
            "content": filtered_users
        }
    )


@user_admin_router.get('/all-staffs', dependencies=[Depends(admin_role_middleware)])
async def get_all_staffs(search: Optional[str] = None,
                         email: Optional[str] = None,
                         phone: Optional[str] = None,
                         staff_status: Optional[UserStatus] = None,
                         is_verified: Optional[bool] = None,
                         sort_by_created_at: Optional[str] = None,
                         warehouse_code: Optional[str] = None,
                         warehouse_role: Optional[WarehouseRole] = None,
                         token_details: dict = Depends(access_token_bearer),
                         skip: int = 0, limit: int = 10,
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
async def get_available_staffs(token_details: dict = Depends(access_token_bearer),
                               skip: int = 0, limit: int = 10,
                               session: AsyncSession = Depends(get_session)):
    available_staffs = await user_service.get_available_staffs_service(session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách nhân viên chưa phân kho",
            "content": available_staffs
        }
    )


@user_admin_router.get('/warehouse/{warehouse_id}/staffs', dependencies=[Depends(admin_role_middleware)])
async def get_staffs_by_warehouse(warehouse_id: str,
                                  token_details: dict = Depends(access_token_bearer),
                                  skip: int = 0, limit: int = 10,
                                  session: AsyncSession = Depends(get_session)):
    staffs = await user_service.get_staffs_by_warehouse_service(warehouse_id, session, skip, limit)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách nhân viên trong kho",
            "content": staffs
        }
    )


@user_admin_router.get('/available-for-offer/{offer_id}', dependencies=[Depends(admin_role_middleware)])
async def get_all_customer_for_offer(offer_id: str,
                                     search: Optional[str] = None,
                                     token_details: dict = Depends(access_token_bearer),
                                     skip: int = 0, limit: int = 10,
                                     session: AsyncSession = Depends(get_session)):
    filtered_users = await user_service.get_all_customer_for_offer_service(offer_id, search, session, skip, limit)

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


@user_admin_router.get('/')
async def get_profile_admin(token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    role = token_details.get('role')

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


@user_admin_router.put('/', dependencies=[Depends(admin_role_middleware)])
async def update_profile_admin(user_update_data: UserUpdateModel,
                               session: AsyncSession = Depends(get_session),
                               token_details: dict = Depends(access_token_bearer)):
    id = token_details['user']['id']
    updated_user = await user_service.update_profile_service(id, user_update_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật thông tin người dùng thành công",
            "content": {
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "phone": updated_user.phone
            }
        }
    )


@user_customer_router.put('/', dependencies=[Depends(customer_role_middleware)])
async def update_profile_customer(user_update_data: UserUpdateModel,
                                  session: AsyncSession = Depends(get_session),
                                  token_details: dict = Depends(access_token_bearer)):
    id = token_details['user']['id']
    updated_user = await user_service.update_profile_service(id, user_update_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật thông tin người dùng thành công",
            "content": {
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "phone": updated_user.phone
            }
        }
    )


@user_customer_router.get('/', dependencies=[Depends(customer_role_middleware)])
async def get_profile_customer(token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    filtered_user = await user_service.get_profile_customer_service(user_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin người dùng",
            "content": filtered_user
        }
    )


@user_admin_router.delete('/{id}', dependencies=[Depends(admin_role_middleware)])
async def delete_user(id: str, token_details: dict = Depends(access_token_bearer),
                      session: AsyncSession = Depends(get_session)):
    user_id = await user_service.delete_user(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa người dùng thành công",
            "content": {
                "id": user_id
            }
        }
    )


@user_admin_router.post('/delete', dependencies=[Depends(admin_role_middleware)])
async def delete_multiple_user(data: UserDeleteModel, token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    user_id = await user_service.delete_multiple_user(data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa người dùng thành công",
            "content": {
                "user_ids": user_id
            }
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
