from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH
import json
import uuid
import os
from src.database.models import Province, Ward

PROVINCE_JSON_PATH="D:/python/E-Commerce/Backend/seeds/data/province.json"
WARD_JSON_PATH="D:/python/E-Commerce/Backend/seeds/data/ward.json"

class ImportAllDataService:
    def load_nested_divisions(self):
        with open(NESTED_DIVISIONS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    # async def import_all_data(self, session: AsyncSession):
    #     divisions_data = self.load_nested_divisions()
    #
    #     all_province_codes = [p['code'] for p in divisions_data]
    #     result = await session.exec(
    #         select(Province.code).where(Province.code.in_(all_province_codes))
    #     )
    #     existing_province_codes = set(result.all())
    #
    #     new_provinces = [
    #         Province(
    #             code=p['code'],
    #             name=p['name'],
    #             code_name=p['codename'],
    #             division_type=p['division_type'],
    #             phone_code=p['phone_code'],
    #         )
    #         for p in divisions_data
    #         if p['code'] not in existing_province_codes
    #     ]
    #     if new_provinces:
    #         session.add_all(new_provinces)
    #     await session.commit()
    #
    #     result = await session.exec(
    #         select(Province.code, Province.id).where(Province.code.in_(all_province_codes))
    #     )
    #     province_map = {code: pid for code, pid in result.all()}
    #
    #     all_ward_codes = [
    #         w['code']
    #         for p in divisions_data
    #         for w in p.get('wards', [])
    #     ]
    #     existing_ward_codes: set = set()
    #     if all_ward_codes:
    #         result = await session.exec(
    #             select(Ward.code).where(Ward.code.in_(all_ward_codes))
    #         )
    #         existing_ward_codes = set(result.all())
    #
    #     new_wards = [
    #         Ward(
    #             code=w['code'],
    #             name=w['name'],
    #             code_name=w['codename'],
    #             short_code_name=w['short_codename'],
    #             division_type=w['division_type'],
    #             province_id=province_map[p['code']],
    #         )
    #         for p in divisions_data
    #         if p['code'] in province_map
    #         for w in p.get('wards', [])
    #         if w['code'] not in existing_ward_codes
    #     ]
    #     if new_wards:
    #         session.add_all(new_wards)
    #     await session.commit()
    #
    #     return {
    #         "provinces_created": len(new_provinces),
    #         "wards_created": len(new_wards),
    #         "total_provinces": len(divisions_data),
    #     }

    def load_json_file(self, path: str) -> list:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        return []

    def save_json_file(self, path: str, data: list):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_all_data(self):
        divisions_data = self.load_nested_divisions()

        # --- Xử lý Provinces ---
        existing_provinces = self.load_json_file(PROVINCE_JSON_PATH)
        existing_province_codes = {p['code'] for p in existing_provinces}

        new_provinces = [
            {
                "id": str(uuid.uuid4()),  # sinh UUID ngẫu nhiên
                "code": p['code'],
                "name": p['name'],
                "code_name": p['codename'],
                "division_type": p['division_type'],
                "phone_code": p['phone_code'],
            }
            for p in divisions_data
            if p['code'] not in existing_province_codes
        ]

        all_provinces = existing_provinces + new_provinces
        self.save_json_file(PROVINCE_JSON_PATH, all_provinces)

        # Map province_code -> uuid id
        province_map = {p['code']: p['id'] for p in all_provinces}

        # --- Xử lý Wards ---
        existing_wards = self.load_json_file(WARD_JSON_PATH)
        existing_ward_codes = {w['code'] for w in existing_wards}

        new_wards = [
            {
                "id": str(uuid.uuid4()),  # sinh UUID ngẫu nhiên
                "code": w['code'],
                "name": w['name'],
                "code_name": w['codename'],
                "short_code_name": w['short_codename'],
                "division_type": w['division_type'],
                "province_id": province_map[p['code']],  # UUID của province
            }
            for p in divisions_data
            if p['code'] in province_map
            for w in p.get('wards', [])
            if w['code'] not in existing_ward_codes
        ]

        all_wards = existing_wards + new_wards
        self.save_json_file(WARD_JSON_PATH, all_wards)

        return {
            "provinces_created": len(new_provinces),
            "wards_created": len(new_wards),
            "total_provinces": len(divisions_data),
        }


