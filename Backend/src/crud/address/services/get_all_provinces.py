from typing import Optional
from sqlmodel import desc, asc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.address.repositories import AddressRepository
from src.database.models import Province

address_repository = AddressRepository()

class GetAllProvincesService:
    async def get_all_provinces(self, session: AsyncSession, search: Optional[str] = None):
        where_conditions = []
        if search:
            search_term = search.lower().strip()
            where_conditions.append(
                Province.name.ilike(f"%{search_term}%") |
                Province.code_name.contains(search_term)
            )

        order_by = asc(Province.name)

        provinces = await address_repository.get_all_provinces(session=session, where_conditions=where_conditions, order_by=order_by)

        return [
            {
                "id": str(p.id),
                "code": p.code,
                "name": p.name,
                "code_name": p.code_name,
                "division_type": p.division_type,
                "phone_code": p.phone_code
            }
            for p in provinces
        ]