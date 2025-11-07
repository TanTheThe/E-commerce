from sqlmodel import desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.address.repositories import AddressRepository
from src.database.models import Address

address_repository = AddressRepository()

class GetAllAddressesService:
    async def get_all_addresses(self, user_id: str, session: AsyncSession):
        order_by = desc(Address.created_at)
        condition = [Address.user_id == user_id, Address.deleted_at.is_(None)]
        addresses = await address_repository.get_all_addresses(session, where_conditions=condition, order_by=order_by)

        addresses_data = [
            {
                "id": str(address.id),
                "line": address.line,
                "street": address.street,
                "ward": address.ward,
                "city": address.city,
                "district": address.district,
                "country": address.country,
                "created_at": address.created_at.isoformat() if address.created_at else None,
            } for address in addresses
        ]

        return addresses_data

