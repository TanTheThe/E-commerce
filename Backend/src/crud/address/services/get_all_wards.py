from typing import Optional
from sqlmodel import asc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.address.repositories import AddressRepository
from src.database.models import Province, Ward
from src.errors.address import AddressException

address_repository = AddressRepository()

class GetAllWardsService:
    async def get_all_wards(self, province_id: str, session: AsyncSession, search: Optional[str] = None):
        condition_province = [Province.id == province_id]
        province = await address_repository.get_province(session=session, where_conditions=condition_province)
        if not province:
            AddressException.province_not_found()

        where_conditions = [Ward.province_id == province_id]
        if search:
            search_term = search.lower().strip()
            where_conditions.append(
                Ward.name.ilike(f"%{search_term}%") |
                Ward.code_name.contains(search_term) |
                Ward.short_code_name.contains(search_term)
            )

        order_by = asc(Ward.name)

        wards = await address_repository.get_all_wards(session=session, where_conditions=where_conditions, order_by=order_by)

        return [
            {
                "id": str(w.id),
                "code": w.code,
                "name": w.name,
                "code_name": w.code_name,
                "division_type": w.division_type,
                "short_code_name": w.short_code_name,
            }
            for w in wards
        ]