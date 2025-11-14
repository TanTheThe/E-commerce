from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH
import json

from src.database.models import Province, Ward


class ImportAllDataService:
    def load_nested_divisions(self):
        with open(NESTED_DIVISIONS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    async def import_all_data(self, session: AsyncSession):
        divisions_data = self.load_nested_divisions()
        provinces_created = 0
        wards_created = 0

        for province_data in divisions_data:
            statement = select(Province).where(Province.code == province_data['code'])
            result = await session.exec(statement)
            existing_province = result.one_or_none()

            if not existing_province:
                province = Province(
                    code=province_data['code'],
                    name=province_data['name'],
                    code_name=province_data['codename'],
                    division_type=province_data['division_type'],
                    phone_code=province_data['phone_code']
                )
                session.add(province)
                provinces_created += 1

        await session.commit()

        for province_data in divisions_data:
            statement_province = select(Province).where(Province.code == province_data['code'])
            result = await session.exec(statement_province)
            province = result.one_or_none()

            if not province:
                continue

            for ward_data in province_data.get('wards', []):
                statement = select(Ward).where(Ward.code == ward_data['code'])
                result = await session.exec(statement)
                existing_ward = result.one_or_none()

                if not existing_ward:
                    ward = Ward(
                        code=ward_data['code'],
                        name=ward_data['name'],
                        code_name=ward_data['codename'],
                        short_code_name=ward_data['short_codename'],
                        division_type=ward_data['division_type'],
                        province_id=province.id
                    )
                    session.add(ward)
                    wards_created += 1

        await session.commit()

        return {
            "provinces_created": provinces_created,
            "wards_created": wards_created,
            "total_provinces": len(divisions_data)
        }


