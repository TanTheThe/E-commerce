from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.address.repositories import AddressRepository
from src.database.models import Address

address_repository = AddressRepository()

class DeleteAddressService:
    async def delete_address(self, address_id: str, user_id: str, session: AsyncSession):
        condition = [
            Address.id == address_id,
            Address.user_id == user_id,
            Address.deleted_at.is_(None)
        ]

        await address_repository.delete_address(condition, session)

