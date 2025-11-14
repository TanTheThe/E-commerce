from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.address.repositories import AddressRepository
from src.database.models import Province, Ward
from src.errors.address import AddressException
from src.schemas.address import AddressCreateModel
import uuid

address_repository = AddressRepository()

class CreateAddressService:
    async def create_address(self, address_data: AddressCreateModel, user_id: str, session: AsyncSession):
        condition_province = [Province.id == address_data.province_id]
        province = await address_repository.get_province(session=session, where_conditions=condition_province)

        if not province:
            AddressException.province_not_found()

        condition_province = [Ward.id == address_data.ward_id, Ward.province_id == address_data.province_id]
        ward = await address_repository.get_ward(session=session, where_conditions=condition_province)

        if not ward:
            AddressException.ward_not_found()

        address_dict = {
            "id": uuid.uuid4(),
            "line": address_data.line,
            "ward_id": address_data.ward_id,
            "province_id": address_data.province_id,
            "country": address_data.country,
            "created_at": datetime.now(),
            "user_id": user_id
        }

        new_address = await address_repository.create_address(address_dict, session)

        await session.commit()

        return {
            "id": str(new_address.id),
            "line": new_address.line,
            "country": new_address.country,
            "created_at": new_address.created_at.isoformat() if new_address.created_at else None,
            "province_info": {
                    "id": str(province.id),
                    "name": province.name,
                    "code": province.code,
                    "code_name": province.code_name,
                    "division_type": province.division_type,
                    "phone_code": province.phone_code
                },
                "ward_info": {
                    "id": str(ward.id),
                    "name": ward.name,
                    "code": ward.code,
                    "code_name": ward.code_name,
                    "division_type": ward.division_type
                }
        }