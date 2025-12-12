from datetime import datetime
from fastapi import APIRouter, status, Depends, Query
from typing import Optional, Literal
from src.crud.notification.services.get_notifications import GetNotificationsService
from src.crud.notification.services.mark_as_processed import MarkAsProcessedService
from src.crud.notification.services.mark_as_read import MarkAsReadService

from src.dependencies import AccessTokenBearer, customer_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.errors.notification import NotificationException
from src.schemas.notification import MarkAsReadRequest, MarkAsProcessedRequest, NotificationType, SenderType

notification_admin_router = APIRouter(prefix="/notification")
notification_customer_router = APIRouter(prefix="/notification")
notification_staff_router = APIRouter(prefix="/notification")


mark_as_processed_service = MarkAsProcessedService()
mark_as_read_service = MarkAsReadService()
get_notifications_service = GetNotificationsService()
access_token_bearer = AccessTokenBearer()

@notification_admin_router.post("/mark-read", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def mark_admin_notifications_read(request: MarkAsReadRequest,
                                        token_details: dict = Depends(access_token_bearer),
                                        session: AsyncSession = Depends(get_session)):
    result = await mark_as_read_service.mark_as_read_for_admin(session, request.notification_ids)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đã đánh dấu {result['count']} thông báo đã đọc",
            "content": result
        }
    )

@notification_admin_router.post("/mark-processed", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def mark_notification_processed(request: MarkAsProcessedRequest,
                                      token_details: dict = Depends(access_token_bearer),
                                      session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    user_email = token_details['user']['email']
    result = await mark_as_processed_service.mark_as_processed(session, request.notification_id, user_id, user_email)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Đã đánh dấu thông báo đã xử lý",
            "content": result
        }
    )

@notification_admin_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_admin_notifications(unread_only: bool = Query(False, description="Chỉ lấy thông báo chưa đọc"),
                                action_required: bool = Query(False, description="Chỉ lấy thông báo cần action"),
                                is_processed: Optional[bool] = Query(None, description="Lọc theo trạng thái xử lý"),
                                notification_type: Optional[str] = Query(None, description="Lọc theo loại thông báo"),
                                sender_type: Optional[str] = Query(None, description="Lọc theo loại người gửi"),
                                from_date: Optional[datetime] = Query(None, description="Lọc từ ngày"),
                                to_date: Optional[datetime] = Query(None, description="Lọc đến ngày"),
                                sort_by: Literal["created_at", "read_at"] = Query("created_at", description="Sắp xếp theo"),
                                sort_order: Literal["asc", "desc"] = Query("desc", description="Thứ tự"),
                                skip: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=100),
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    if from_date and to_date and from_date > to_date:
        NotificationException.invalid_date_filter()

    if notification_type:
        valid_types = [
            NotificationType.ORDER_STATUS,
            NotificationType.ORDER_CANCELLATION_REQUEST,
            NotificationType.RETURN_ORDER_REQUEST,
            NotificationType.SPECIAL_OFFER,
        ]
        if notification_type not in valid_types:
            NotificationException.notification_type_invalid(valid_types)

    if sender_type:
        valid_sender_types = [SenderType.ADMIN, SenderType.CUSTOMER]
        if sender_type not in valid_sender_types:
            NotificationException.notification_type_invalid(valid_sender_types)

    notis_dict = await get_notifications_service.get_notifications_admin(session=session,
                                                                        unread_only=unread_only,
                                                                        action_required=action_required,
                                                                        is_processed=is_processed,
                                                                        notification_type=notification_type,
                                                                        sender_type=sender_type,
                                                                        from_date=from_date,
                                                                        to_date=to_date,
                                                                        sort_by=sort_by,
                                                                        sort_order=sort_order,
                                                                        skip=skip,
                                                                        limit=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin toàn bộ thông báo",
            "content": notis_dict
        }
    )


@notification_customer_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_role_middleware)])
async def get_customer_notifications(unread_only: bool = Query(False, description="Chỉ lấy thông báo chưa đọc"),
                                    notification_type: Optional[str] = Query(None, description="Lọc theo loại thông báo"),
                                    from_date: Optional[datetime] = Query(None, description="Lọc từ ngày"),
                                    to_date: Optional[datetime] = Query(None, description="Lọc đến ngày"),
                                    sort_by: Literal["created_at", "read_at"] = Query("created_at", description="Sắp xếp theo"),
                                    sort_order: Literal["asc", "desc"] = Query("desc", description="Thứ tự"),
                                    skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100),
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']

    if from_date and to_date and from_date > to_date:
        NotificationException.invalid_date_filter()

    if notification_type:
        valid_types = [
            NotificationType.ORDER_STATUS,
            NotificationType.ORDER_CANCELLATION_REQUEST,
            NotificationType.RETURN_ORDER_REQUEST,
            NotificationType.SPECIAL_OFFER,
        ]
        if notification_type not in valid_types:
            NotificationException.notification_type_invalid(valid_types)

    notis_dict = await get_notifications_service.get_notifications_customer(session=session,
                                                                            user_id=user_id,
                                                                            unread_only=unread_only,
                                                                            notification_type=notification_type,
                                                                            from_date=from_date,
                                                                            to_date=to_date,
                                                                            sort_by=sort_by,
                                                                            sort_order=sort_order,
                                                                            skip=skip,
                                                                            limit=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin toàn bộ thông báo",
            "content": notis_dict
        }
    )


@notification_customer_router.post("/mark-read", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_role_middleware)])
async def mark_customer_notifications_read(request: MarkAsReadRequest,
                                        token_details: dict = Depends(access_token_bearer),
                                        session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    result = await mark_as_read_service.mark_as_read_for_customer(session, request.notification_ids, user_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đã đánh dấu {result['count']} thông báo đã đọc",
            "content": result
        }
    )

@notification_customer_router.post("/mark-all-read", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_role_middleware)])
async def mark_all_customer_notifications_read(token_details: dict = Depends(access_token_bearer),
                                             session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    count = await mark_as_read_service.mark_all_as_read_for_customer(session, user_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đã đánh dấu tất cả thông báo đã đọc",
            "content": {
                "marked_count": count
            }
        }
    )








