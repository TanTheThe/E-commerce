from sqlalchemy.orm import selectinload
from sqlmodel import desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.address.repositories import AddressRepository
from src.database.models import Address

address_repository = AddressRepository()

class GetAllAddressesService:
    async def get_all_addresses(self, user_id: str, session: AsyncSession):
        order_by = desc(Address.created_at)
        condition = [Address.user_id == user_id, Address.deleted_at.is_(None)]
        options = [selectinload(Address.province), selectinload(Address.ward)]
        addresses, _ = await address_repository.get_all_addresses(session, where_conditions=condition, order_by=order_by, options=options)

        addresses_data = [
            {
                "id": str(address.id),
                "line": address.line,
                "country": address.country,
                "created_at": address.created_at.isoformat() if address.created_at else None,
                "province_info": {
                    "id": str(address.province.id),
                    "name": address.province.name,
                    "code": address.province.code,
                    "code_name": address.province.code_name,
                    "division_type": address.province.division_type,
                    "phone_code": address.province.phone_code
                },
                "ward_info": {
                    "id": str(address.ward.id) if address.ward else None,
                    "name": address.ward.name,
                    "code": address.ward.code,
                    "code_name": address.ward.code_name,
                    "division_type": address.ward.division_type
                }
            } for address in addresses
        ]

        return addresses_data

