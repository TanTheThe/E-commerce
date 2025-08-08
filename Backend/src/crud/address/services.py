from src.database.models import Address
from src.schemas.address import AddressCreateModel, AddressUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.crud.address.repositories import AddressRepository
from src.errors.address import AddressException

address_repository = AddressRepository()

class AddressService:
    async def create_new_address_service(self, user_id, address_data: AddressCreateModel, session: AsyncSession):
        new_address = await address_repository.create_address(user_id, address_data, session)

        new_address_dict = {
            "id": str(new_address.id),
            "line": new_address.line,
            "street": new_address.street,
            "ward": new_address.ward,
            "city": new_address.city,
            "district": new_address.district,
            "country": new_address.country
        }
        return new_address_dict


    async def get_all_address_service(self, user_id, session: AsyncSession):
        condition = and_(Address.user_id == user_id)
        addresses = await address_repository.get_all_address(condition, session)

        if len(addresses) == 0:
            AddressException.empty_list()

        filtered_address = [
            {
                "id": str(address.id),
                "line": address.line,
                "street": address.street,
                "ward": address.ward,
                "city": address.city,
                "district": address.district,
                "country": address.country
            }
            for address in addresses
        ]
        return filtered_address


    async def update_address_service(self, id: str, customer_id: str, address_update: AddressUpdateModel, session: AsyncSession):
        condition = and_(Address.id == id, Address.user_id == customer_id)
        addresses = await address_repository.get_address(condition, session)

        if not addresses:
            AddressException.not_found()

        await address_repository.update_address(addresses, address_update.model_dump(exclude_none=True), session)
        await session.commit()

        address_dict = {
            "id": str(id),
            **address_update.model_dump(exclude_none=True),
        }

        return address_dict


    async def delete_address(self, id: str, session: AsyncSession):
        condition = and_(Address.id == id)
        return await address_repository.delete_address(condition, session)


