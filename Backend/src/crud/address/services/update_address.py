from functools import lru_cache
import json
from sqlalchemy.ext.asyncio import AsyncSession
from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH

from src.crud.address.repositories import AddressRepository
from src.database.models import Address
from src.errors.address import AddressException
from src.schemas.address import AddressUpdateModel

address_repository = AddressRepository()

class UpdateAddressService:
    async def update_address(self, address_id: str, customer_id: str,
                                     address_update: AddressUpdateModel, session: AsyncSession):
        condition = [Address.id == address_id, Address.customer_id == customer_id, Address.deleted_at.is_(None)]
        address_data = await address_repository.get_address(session, where_conditions=condition)

        if not address_data:
            AddressException.not_found()

        if address_update.country == "Việt Nam":
            city = address_update.city if address_update.city is not None else address_data.city
            district = address_update.district if address_update.district is not None else address_data.district
            ward = address_update.ward if address_update.ward is not None else address_data.ward

            if city and district and ward:
                is_valid = await self.validate_vn_address(city, district, ward)
                if not is_valid:
                    AddressException.invalid_address()

        update_data = address_update.model_dump(exclude_unset=True)

        address_result = await address_repository.update_address(condition, update_data, session)

        await session.commit()

        return {
            "line": address_result.line if address_result.line else None,
            "street": address_result.street if address_result.street else None,
            "ward": address_result.ward if address_result.ward else None,
            "city": address_result.city if address_result.city else None,
            "district": address_result.district if address_result.district else None,
            "country": address_result.country if address_result.country else None,
        }

    @lru_cache(maxsize=1)
    def load_nested_divisions(self):
        with open(NESTED_DIVISIONS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    @lru_cache(maxsize=1000)
    async def validate_vn_address(self, city: str, district: str, ward: str):
        try:
            divisions_data = self.load_nested_divisions()

            city_normalized = self.normalize_text(city)
            district_normalized = self.normalize_text(district)
            ward_normalized = self.normalize_text(ward)

            province_found = None
            for province in divisions_data:
                province_name_normalized = self.normalize_text(province['name'])
                if city_normalized in province_name_normalized or province_name_normalized in city_normalized:
                    province_found = province
                    break

            if not province_found:
                return False

            district_found = None
            for district_obj in province_found.get('districts', []):
                district_name_normalized = self.normalize_text(district_obj['name'])
                if district_normalized in district_name_normalized or district_name_normalized in district_normalized:
                    district_found = district_obj
                    break

            if not district_found:
                return False

            for ward_obj in district_found.get('wards', []):
                ward_name_normalized = self.normalize_text(ward_obj['name'])
                if ward_normalized in ward_name_normalized or ward_name_normalized in ward_normalized:
                    return True

            return False

        except Exception as e:
            return False

    def normalize_text(self, text: str):
        text = text.lower().strip()

        prefixes = [
            'tỉnh', 'thành phố', 'tp.', 'tp', 'quận', 'huyện', 'thị xã', 'phường', 'xã', 'thị trấn', 'tt.', 'tt'
        ]

        for prefix in prefixes:
            if text.startswith(prefix + ' '):
                text = text[len(prefix):].strip()
            elif text.startswith(prefix + '.'):
                text = text[len(prefix) + 1:].strip()

        return text



