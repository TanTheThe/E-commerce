from fastapi import APIRouter, status, Depends
from src.crud.address.services.create_address import CreateAddressService
from src.crud.address.services.delete_address import DeleteAddressService
from src.crud.address.services.get_all_address import GetAllAddressesService
from src.crud.address.services.update_address import UpdateAddressService
from src.database.main import get_session
from src.dependencies import AccessTokenBearer
from src.schemas.address import AddressCreateModel, AddressUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import JSONResponse
from src.dependencies import customer_role_middleware

address_admin_router = APIRouter(prefix="/address")
address_customer_router = APIRouter(prefix="/address")
address_staff_router = APIRouter(prefix="/address")

create_address_service = CreateAddressService()
get_all_addresses_service = GetAllAddressesService()
update_address_service = UpdateAddressService()
delete_address_service = DeleteAddressService()
access_token_bearer = AccessTokenBearer()


@address_customer_router.post('/', dependencies=[Depends(customer_role_middleware)], response_model=None)
async def create_address(address_data: AddressCreateModel, session: AsyncSession = Depends(get_session),
                         token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    new_address = await create_address_service.create_address(address_data, user_id, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Tạo địa chỉ mới thành công",
            "content": new_address
        }
    )


@address_customer_router.get('/', dependencies=[Depends(customer_role_middleware)])
async def get_all_addresses(session: AsyncSession = Depends(get_session),
                            token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    addresses_data = await get_all_addresses_service.get_all_addresses(user_id, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Thông tin các địa chỉ của người dùng",
            "content": addresses_data
        }
    )


@address_customer_router.put('/{address_id}', dependencies=[Depends(customer_role_middleware)])
async def update_address(address_id: str, address_data: AddressUpdateModel,
                         session: AsyncSession = Depends(get_session),
                         token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    address_result = await update_address_service.update_address(address_id, user_id, address_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Thông tin địa chỉ sau khi cập nhật",
            "content": address_result
        }
    )


@address_customer_router.delete('/{address_id}', dependencies=[Depends(customer_role_middleware)])
async def delete_address(address_id: str, session: AsyncSession = Depends(get_session),
                         token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    await delete_address_service.delete_address(address_id, user_id, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Xóa địa chỉ của người dùng thành công",
        }
    )



















