from fastapi import APIRouter, status, Depends
from typing import Optional
from src.crud.notification.services import NotificationService
from src.dependencies import AccessTokenBearer, customer_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.schemas.notification import MarkAsReadRequest, MarkAsProcessedRequest

notification_admin_router = APIRouter(prefix="/notification")
notification_customer_router = APIRouter(prefix="/notification")
notification_common_router = APIRouter(prefix="/notification")

notification_service = NotificationService()
access_token_bearer = AccessTokenBearer()

@notification_admin_router.post("/mark-read", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def mark_admin_notifications_read(request: MarkAsReadRequest,
                                        token_details: dict = Depends(access_token_bearer),
                                        session: AsyncSession = Depends(get_session)):
    count = await notification_service.mark_as_read(session, request.notification_ids)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đã đánh dấu {count} thông báo đã đọc",
            "content": {
                "marked_count": count
            }
        }
    )

@notification_admin_router.post("/mark-processed", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def mark_notification_processed(request: MarkAsProcessedRequest,
                                      token_details: dict = Depends(access_token_bearer),
                                      session: AsyncSession = Depends(get_session)):
    success = await notification_service.mark_as_processed(session, request.notification_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Đã đánh dấu thông báo đã xử lý",
            "content": {"notification_id": request.notification_id}
        }
    )

@notification_admin_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_admin_notifications(unread_only: bool = False,
                                  action_required: bool = False,
                                  skip: int = 0, limit: int = 30,
                                  token_details: dict = Depends(access_token_bearer),
                                  session: AsyncSession = Depends(get_session)):
    notis_dict = await notification_service.get_notifications_admin_service(session, unread_only, action_required, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin toàn bộ thông báo",
            "content": notis_dict
        }
    )

@notification_admin_router.get("/unread-count", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_admin_unread_count(token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    count = await notification_service.get_unread_count_service(session, recipient_type="admin")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin toàn bộ thông báo",
            "content": {
                "unread_count": count
            }
        }
    )

@notification_admin_router.get("/pending-actions-count", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_pending_actions_count(action_type: Optional[str] = None,
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    count = await notification_service.get_pending_actions_count(session, action_type)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Số lượng thông báo cần xử lý",
            "content": {
                "pending_actions_count": count,
                "action_type": action_type
            }
        }
    )

@notification_customer_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_role_middleware)])
async def get_customer_notifications(unread_only: bool = False,
                                     skip: int = 0, limit: int = 30,
                                     token_details: dict = Depends(access_token_bearer),
                                     session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    notis_dict = await notification_service.get_notifications_customer_service(session, user_id, unread_only, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin toàn bộ thông báo",
            "content": notis_dict
        }
    )

@notification_customer_router.get("/unread-count", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_role_middleware)])
async def get_customer_unread_count(token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    count = await notification_service.get_unread_count_service(session, recipient_type="customer", user_id=user_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin toàn bộ thông báo",
            "content": {
                "unread_count": count
            }
        }
    )

@notification_customer_router.post("/mark-read", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_role_middleware)])
async def mark_customer_notifications_read(request: MarkAsReadRequest,
                                        token_details: dict = Depends(access_token_bearer),
                                        session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    count = await notification_service.mark_as_read(session, request.notification_ids, user_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đã đánh dấu {count} thông báo đã đọc",
            "content": {
                "marked_count": count
            }
        }
    )

@notification_customer_router.post("/mark-all-read", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_role_middleware)])
async def mark_all_customer_notifications_read(token_details: dict = Depends(access_token_bearer),
                                             session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    count = await notification_service.mark_all_as_read(session, user_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đã đánh dấu tất cả thông báo đã đọc",
            "content": {
                "marked_count": count
            }
        }
    )








