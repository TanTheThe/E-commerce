from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.crud.address.repositories import AddressRepository
from src.database.models import Address, Province, Ward
from src.errors.address import AddressException
from src.schemas.address import AddressUpdateModel

address_repository = AddressRepository()

class UpdateAddressService:
    async def update_address(self, address_id: str, customer_id: str,
                             address_update: AddressUpdateModel, session: AsyncSession):
        condition = [Address.id == address_id, Address.user_id == customer_id, Address.deleted_at.is_(None)]
        options = [selectinload(Address.province), selectinload(Address.ward)]
        address_data = await address_repository.get_address(session, where_conditions=condition, options=options)

        if not address_data:
            AddressException.not_found()

        new_province = None
        new_ward = None

        if address_update.province_id is not None and address_update.ward_id is not None:
            condition_province = [Province.id == address_update.province_id]
            new_province = await address_repository.get_province(session, where_conditions=condition_province)
            if not new_province:
                AddressException.province_not_found()

            condition_ward = [Ward.id == address_update.ward_id]
            new_ward = await address_repository.get_ward(session, where_conditions=condition_ward)
            if not new_ward:
                AddressException.ward_not_found()

        if address_update.line is not None:
            address_data.line = address_update.line

        if address_update.country is not None:
            address_data.country = address_update.country

        address_data.updated_at = datetime.now()

        session.add(address_data)
        await session.commit()
        await session.refresh(address_data)

        province_info = new_province if new_province else address_data.province
        ward_info = new_ward if new_ward else address_data.ward

        return {
            "id": str(address_data.id),
            "line": address_data.line,
            "country": address_data.country,
            "created_at": address_data.created_at.isoformat() if address_data.created_at else None,
            "province_info": {
                "id": str(province_info.id),
                "name": province_info.name,
                "code": province_info.code,
                "code_name": province_info.code_name,
                "division_type": province_info.division_type,
                "phone_code": province_info.phone_code
            } if province_info else None,
            "ward_info": {
                "id": str(ward_info.id),
                "name": ward_info.name,
                "code": ward_info.code,
                "code_name": ward_info.code_name,
                "division_type": ward_info.division_type
            } if ward_info else None
        }




