from fastapi import APIRouter, status, Depends
from typing import Optional
from src.crud.evaluate.services import EvaluateService
from src.dependencies import AccessTokenBearer
from src.schemas.evaluate import EvaluateInputModel, SupplementEvaluateModel, GetEvaluateByProduct, EvaluateFilterModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware, customer_role_middleware

evaluate_admin_router = APIRouter(prefix="/evaluate")
evaluate_customer_router = APIRouter(prefix="/evaluate")
evaluate_common_router = APIRouter(prefix="/evaluate")

evaluate_service = EvaluateService()
access_token_bearer = AccessTokenBearer()


@evaluate_customer_router.post("/", status_code=status.HTTP_201_CREATED,
                               dependencies=[Depends(customer_role_middleware)])
async def create_evaluate(evaluate_data: EvaluateInputModel,
                          token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):
    customer_id = token_details["user"]["id"]
    new_evaluate_dict = await evaluate_service.create_evaluate_service(customer_id, evaluate_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Đánh giá mới vừa được thêm vào",
            "content": new_evaluate_dict
        }
    )


@evaluate_customer_router.get("/my-reviews", status_code=status.HTTP_200_OK,
                              dependencies=[Depends(customer_role_middleware)])
async def get_my_evaluates(token_details: dict = Depends(access_token_bearer),
                           session: AsyncSession = Depends(get_session)):
    customer_id = token_details["user"]["id"]
    evaluate_dict = await evaluate_service.get_evaluates_by_customer(customer_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách đánh giá của bạn",
            "content": evaluate_dict
        }
    )


@evaluate_admin_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_all_evaluate_admin(search: Optional[str] = None,
                                 rate: Optional[int] = None,
                                 sort_by_created_at: Optional[str] = None,
                                 sort_by_rate: Optional[str] = None,
                                 skip: int = 0, limit: int = 10,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    filter_data = EvaluateFilterModel(search=search, rate=rate, sort_by_rate=sort_by_rate, sort_by_created_at=sort_by_created_at)
    evaluate_dict = await evaluate_service.get_all_evaluate_admin(filter_data, session, skip, limit)

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
    evaluate_dict = await evaluate_service.get_detail_evaluate_admin(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết đánh giá",
            "content": evaluate_dict
        }
    )


@evaluate_customer_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_evaluate_customer(skip: int = 0, limit: int = 10,
                                    session: AsyncSession = Depends(get_session)):
    evaluate_dict = await evaluate_service.get_all_evaluate_customer(session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các đánh giá",
            "content": evaluate_dict
        }
    )


@evaluate_customer_router.get("/by-product/{product_id}", status_code=status.HTTP_200_OK)
async def get_evaluate_by_product(product_id: str, data: GetEvaluateByProduct,
                                  skip: int = 0, limit: int = 10,
                                  session: AsyncSession = Depends(get_session)):
    evaluate_list = await evaluate_service.get_evaluate_by_product(product_id, data, session, skip, limit)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách đánh giá của sản phẩm",
            "content": evaluate_list
        }
    )


@evaluate_customer_router.get("/average-rate/{product_id}", status_code=status.HTTP_200_OK)
async def get_average_rate(product_id: str,
                           session: AsyncSession = Depends(get_session)):
    avg_rate = await evaluate_service.get_average_rate(product_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Điểm đánh giá trung bình",
            "average_rate": avg_rate
        }
    )


@evaluate_customer_router.patch("/{id}/supplement", dependencies=[Depends(customer_role_middleware)])
async def supplement_evaluate(id: str, data: SupplementEvaluateModel,
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    customer_id = token_details["user"]["id"]
    await evaluate_service.supplement_evaluate(id, customer_id, data, session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Bổ sung đánh giá thành công"}
    )


@evaluate_admin_router.delete('/{id}', dependencies=[Depends(admin_role_middleware)])
async def delete_evaluate(id: str, token_details: dict = Depends(access_token_bearer),
                          session: AsyncSession = Depends(get_session)):
    evaluate_deleted = await evaluate_service.delete_evaluate(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa đánh giá thành công",
            "content": evaluate_deleted
        }
    )
