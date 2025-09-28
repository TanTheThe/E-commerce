from fastapi import APIRouter, status, Depends, BackgroundTasks
from src.dependencies import AccessTokenBearer
from src.schemas.user import UserCreateModel, AdminUpdateModel, ChangePasswordModel, \
    UserUpdateModel, UserDeleteModel, FilterUserInputModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from src.crud.user.services import UserService
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware, customer_role_middleware
from fastapi.responses import RedirectResponse
from typing import Optional
from datetime import datetime

user_service = UserService()
access_token_bearer = AccessTokenBearer()

user_admin_router = APIRouter(prefix="/user")
user_customer_router = APIRouter(prefix="/user")
user_staff_router = APIRouter(prefix="/user")


@user_admin_router.get('/all', dependencies=[Depends(admin_role_middleware)])
async def get_all_customer(search: Optional[str] = None,
                           email: Optional[str] = None,
                           phone: Optional[str] = None,
                           customer_status: Optional[str] = None,
                           sort_by_created_at: Optional[str] = None,
                           token_details: dict = Depends(access_token_bearer),
                           skip: int = 0, limit: int = 10,
                           session: AsyncSession = Depends(get_session)):
    filter_data = FilterUserInputModel(
        search=search,
        email=email,
        phone=phone,
        customer_status=customer_status,
        sort_by_created_at=sort_by_created_at
    )

    filtered_users = await user_service.get_all_customer_service(filter_data, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin người dùng",
            "content": filtered_users
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


@user_admin_router.put('/{id}', dependencies=[Depends(admin_role_middleware)])
async def update_status_by_admin(id: str, user_update_data: AdminUpdateModel,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    updated_user = await user_service.update_profile_service(id, user_update_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật trạng thái khách hạng thành công",
            "content": {
                "customer_status": updated_user.customer_status
            }
        }
    )


@user_admin_router.get('/{id}', dependencies=[Depends(admin_role_middleware)])
async def get_detail_by_admin(id: str, token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    filtered_user = await user_service.get_detail_admin_service(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin người dùng",
            "content": filtered_user
        }
    )


@user_admin_router.get('/', dependencies=[Depends(admin_role_middleware)])
async def get_profile_admin(token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    filtered_user = await user_service.get_profile_admin_service(user_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin người dùng",
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


@user_admin_router.put('/{id}/change-status', dependencies=[Depends(admin_role_middleware)])
async def change_status_user(id: str, token_details: dict = Depends(access_token_bearer),
                             session: AsyncSession = Depends(get_session)):
    user_block = await user_service.change_status_user(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Chặn người dùng thành công",
            "content": user_block
        }
    )
