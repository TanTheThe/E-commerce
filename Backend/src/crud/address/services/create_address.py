from datetime import datetime
from functools import lru_cache
from sqlmodel.ext.asyncio.session import AsyncSession
from vietnam_provinces import Province, Ward, NESTED_DIVISIONS_JSON_PATH
from src.crud.address.repositories import AddressRepository
from src.errors.address import AddressException
from src.schemas.address import AddressCreateModel
import json

address_repository = AddressRepository()

class CreateAddressService:
    async def create_address(self, address_data: AddressCreateModel, user_id: str, session: AsyncSession):
        if address_data.country == "Việt Nam":
            is_valid = await self.validate_vn_address(
                address_data.city,
                address_data.district,
                address_data.ward
            )
            if not is_valid:
                AddressException.invalid_address()

        address_dict = {
            "line": address_data.line,
            "street": address_data.street,
            "city": address_data.city,
            "ward": address_data.ward,
            "country": address_data.country,
            "district": address_data.district,
            "created_at": datetime.now(),
            "user_id": user_id
        }

        new_address = await address_repository.create_address(address_dict, session)

        await session.commit()

        return {
            "line": new_address.line,
            "street": new_address.street,
            "city": new_address.city,
            "ward": new_address.ward,
            "country": new_address.country,
            "district": new_address.district,
            "created_at": new_address.created_at,
            "user_id": new_address.user_id
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