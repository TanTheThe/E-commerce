from fastapi import APIRouter, status, Depends, Query
from typing import Optional, Literal
from src.crud.evaluate.services.create_evaluate import CreateEvaluateService
from src.crud.evaluate.services.get_all_evaluate import GetAllEvaluateService
from src.crud.evaluate.services.get_detail_evaluate import GetDetailEvaluateService
from src.crud.evaluate.services.remaining_services import RemainingEvaluateService
from src.dependencies import AccessTokenBearer
from src.schemas.evaluate import EvaluateInputModel, SupplementEvaluateModel, EvaluateFilterModel, ReplyEvaluateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware, customer_role_middleware

evaluate_admin_router = APIRouter(prefix="/evaluate")
evaluate_customer_router = APIRouter(prefix="/evaluate")
evaluate_staff_router = APIRouter(prefix="/evaluate")

create_evaluate_service = CreateEvaluateService()
get_all_evaluate_service = GetAllEvaluateService()
get_detail_evaluate_service = GetDetailEvaluateService()
remaining_evaluate_service = RemainingEvaluateService()
access_token_bearer = AccessTokenBearer()


@evaluate_customer_router.post("/", status_code=status.HTTP_201_CREATED,
                               dependencies=[Depends(customer_role_middleware)])
async def create_evaluate(evaluate_data: EvaluateInputModel,
                          token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):
    customer_id = token_details["user"]["id"]
    new_evaluate_dict = await create_evaluate_service.create_evaluate(customer_id, evaluate_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Đánh giá mới vừa được thêm vào",
            "content": new_evaluate_dict
        }
    )


@evaluate_admin_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_all_evaluate_admin(search: Optional[str] = Query(None, description="Tìm kiếm theo tên, mã đơn, sản phẩm", max_length=255),
                                rate: Optional[int] = Query(None, ge=1, le=5, description="Lọc theo số sao (1-5)"),
                                product_id: Optional[str] = Query(None, description="Lọc theo ID sản phẩm"),
                                user_id: Optional[str] = Query(None, description="Lọc theo ID người dùng"),
                                sort_by_created_at: Optional[Literal["newest", "oldest"]] = Query(None, description="Sắp xếp theo thời gian"),
                                sort_by_rate: Optional[Literal["highest", "lowest"]] = Query(None, description="Sắp xếp theo rating"),
                                skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                limit: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    filter_data = EvaluateFilterModel(
        search=search,
        rate=rate,
        product_id=product_id,
        user_id=user_id,
        sort_by_rate=sort_by_rate,
        sort_by_created_at=sort_by_created_at
    )

    evaluate_dict = await get_all_evaluate_service.get_all_evaluate_admin(filter_data, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các đánh giá",
            "content": evaluate_dict
        }
    )


@evaluate_customer_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_evaluate_customer(rate: Optional[int] = Query(None, ge=1, le=5, description="Lọc theo số sao (1-5)"),
                                    product_id: Optional[str] = Query(None, description="Lọc theo ID sản phẩm"),
                                    sort_by_rate: Optional[Literal["highest", "lowest"]] = Query(None, description="Sắp xếp theo rating"),
                                    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                    limit: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
                                    session: AsyncSession = Depends(get_session)):
    filter_data = EvaluateFilterModel(
        rate=rate,
        product_id=product_id,
        sort_by_rate=sort_by_rate,
        search=None,
        sort_by_created_at=None,
        user_id=None
    ) if rate or product_id or sort_by_rate else None

    evaluate_dict = await get_all_evaluate_service.get_all_evaluate_customer(filter_data, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các đánh giá",
            "content": evaluate_dict
        }
    )


@evaluate_admin_router.get("/{id}", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_detail_evaluate_admin(id: str,
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    evaluate_dict = await get_detail_evaluate_service.get_detail_evaluate_admin(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết đánh giá",
            "content": evaluate_dict
        }
    )


@evaluate_customer_router.get("/{id}", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_role_middleware)])
async def get_detail_evaluate_customer(id: str,
                                       token_details: dict = Depends(access_token_bearer),
                                       session: AsyncSession = Depends(get_session)):
    customer_id = token_details["user"]["id"]
    evaluate_dict = await get_detail_evaluate_service.get_detail_evaluate_customer(id, customer_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết đánh giá",
            "content": evaluate_dict
        }
    )


@evaluate_customer_router.put("/{id}/supplement", dependencies=[Depends(customer_role_middleware)])
async def supplement_evaluate(id: str, data: SupplementEvaluateModel,
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    customer_id = token_details["user"]["id"]
    updated_evaluate = await remaining_evaluate_service.supplement_evaluate(id, customer_id, data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Bổ sung đánh giá thành công",
            "content": updated_evaluate
        }
    )


@evaluate_admin_router.put("/{id}/reply", dependencies=[Depends(admin_role_middleware)])
async def reply_evaluate(id: str, data: ReplyEvaluateModel,
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    updated_evaluate = await remaining_evaluate_service.reply_evaluate(id, data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Phản hồi đánh giá thành công",
            "content": updated_evaluate
        }
    )


@evaluate_admin_router.delete('/{id}', dependencies=[Depends(admin_role_middleware)])
async def delete_evaluate(id: str, token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):
    evaluate_deleted = await remaining_evaluate_service.delete_evaluate_service(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa đánh giá thành công",
            "content": evaluate_deleted
        }
    )
