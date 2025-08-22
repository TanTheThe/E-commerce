from fastapi import APIRouter, status, Depends, Query
from typing import List
from src.crud.size.services import SizeService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware

size_admin_router = APIRouter(prefix="/size")
size_customer_router = APIRouter(prefix="/size")
size_common_router = APIRouter(prefix="/size")

size_service = SizeService()
access_token_bearer = AccessTokenBearer()

@size_admin_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_all_size_by_type_size(type_sizes: List[str] = Query(...), token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    sizes_dict = await size_service.get_all_size_by_type_size(type_sizes, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin toàn bộ size",
            "content": sizes_dict
        }
    )





