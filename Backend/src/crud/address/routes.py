from fastapi import APIRouter, status, Depends
from src.crud.address.services import AddressService
from src.dependencies import AccessTokenBearer
from src.schemas.address import AddressCreateModel, AddressUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import customer_role_middleware

address_admin_router = APIRouter(prefix="/address")
address_customer_router = APIRouter(prefix="/address")
address_common_router = APIRouter(prefix="/address")

address_service = AddressService()
access_token_bearer = AccessTokenBearer()


@address_customer_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(customer_role_middleware)])
async def create_new_address(address_data: AddressCreateModel,
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    new_address_dict = await address_service.create_new_address_service(user_id, address_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Địa chỉ mới vừa được thêm vào",
            "content": new_address_dict
        }
    )


@address_customer_router.get('/', dependencies=[Depends(customer_role_middleware)])
async def get_all_address(token_details: dict = Depends(access_token_bearer),
                          session:AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    filtered_address = await address_service.get_all_address_service(user_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin địa chỉ",
            "content": filtered_address
        }
    )


@address_customer_router.put('/{id}', dependencies=[Depends(customer_role_middleware)])
async def update_address(id: str, address_update: AddressUpdateModel,
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    customer_id = token_details['user']['id']
    address_update_dict = await address_service.update_address_service(id, customer_id, address_update, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật địa chỉ thành công",
            "content": address_update_dict
        }
    )


@address_customer_router.delete('/{id}', dependencies=[Depends(customer_role_middleware)])
async def delete_address(id: str,
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    address_delete = await address_service.delete_address(id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa địa chỉ thành công",
            "content": address_delete
        }
    )
















