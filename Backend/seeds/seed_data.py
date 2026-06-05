from __future__ import annotations

import asyncio
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy import select
from sqlmodel import SQLModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.main import async_session_maker, engine
from src.database.models import (
    Address,
    Brand,
    Categories,
    Categories_Product,
    Color,
    Material,
    Permission,
    Product,
    Product_Material,
    Product_Tag,
    Product_Variant,
    Province,
    Role,
    RolePermission,
    Size,
    Special_Offer,
    Supplier,
    Tag,
    User,
    UserRole,
    Ward,
    Warehouse,
)

SEED_DIR = Path(__file__).resolve().parent / "data"

MAIN_MODEL_BY_FILE: dict[str, type[SQLModel]] = {
    "province.json": Province,
    "ward.json": Ward,
    "address.json": Address,
    "brand.json": Brand,
    "categories.json": Categories,
    "color.json": Color,
    "material.json": Material,
    "permission.json": Permission,
    "product.json": Product,
    "product_variant.json": Product_Variant,
    "role.json": Role,
    "size.json": Size,
    "special_offer.json": Special_Offer,
    "supplier.json": Supplier,
    "tag.json": Tag,
    "user.json": User,
    "warehouse.json": Warehouse,
}

JOIN_MODEL_CONFIG: dict[str, dict[str, Any]] = {
    "categories.json": {
        "product_ids": (Categories_Product, "categories_id", "product_id"),
    },
    "product.json": {
        "material_ids": (Product_Material, "product_id", "material_id"),
        "tag_ids": (Product_Tag, "product_id", "tag_id"),
    },
    "role.json": {
        "permission_ids": (RolePermission, "role_id", "permission_id"),
    },
    "user.json": {
        "role_ids": (UserRole, "user_id", "role_id"),
    },
}


def load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return []
    return json.loads(content)


def parse_datetime(value: Any) -> Any:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return value
    return value


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in record.items():
        if key.endswith("_ids"):
            continue
        if isinstance(value, str) and key.endswith(("_at", "_date", "_time")):
            cleaned[key] = parse_datetime(value)
        else:
            cleaned[key] = parse_datetime(value)
    return cleaned


async def existing_ids(session, model: type[SQLModel], ids: Iterable[Any]) -> set[Any]:
    ids = list(ids)
    if not ids:
        return set()
    result = await session.exec(select(model.id).where(model.id.in_(ids)))
    return set(result.all())


async def insert_main_table(session, file_name: str, model: type[SQLModel]) -> dict[str, int]:
    records = load_json(SEED_DIR / file_name)
    if not records:
        return {"inserted": 0, "skipped": 0}

    ids = [item["id"] for item in records if item.get("id")]
    already = await existing_ids(session, model, ids)

    if len(already) == len(ids) and ids:
        return {"inserted": 0, "skipped": len(records)}

    objects = [model(**normalize_record(item)) for item in records if item.get("id") not in already]
    if objects:
        session.add_all(objects)
        await session.commit()

    return {"inserted": len(objects), "skipped": len(records) - len(objects)}


async def insert_join_records(
    session,
    model: type[SQLModel],
    left_fk: str,
    right_fk: str,
    left_id: Any,
    target_ids: Iterable[Any],
) -> int:
    if not target_ids:
        return 0

    target_ids = list(dict.fromkeys(target_ids))
    existing = await session.exec(
        select(model)
        .where(getattr(model, left_fk) == left_id)
        .where(getattr(model, right_fk).in_(target_ids))
    )
    existing_pairs = {
        (getattr(row, left_fk), getattr(row, right_fk))
        for row in existing.all()
    }

    now = datetime.now()
    objs = []
    for related_id in target_ids:
        pair = (left_id, related_id)
        if pair in existing_pairs:
            continue
        objs.append(
            model(
                id=uuid.uuid4(),
                **{left_fk: left_id, right_fk: related_id, "created_at": now}
            )
        )

    if objs:
        session.add_all(objs)
        await session.commit()
    return len(objs)


async def seed_join_table(session, file_name: str, model: type[SQLModel], left_fk: str, right_fk: str, ids_key: str) -> int:
    records = load_json(SEED_DIR / file_name)
    total = 0
    for record in records:
        total += await insert_join_records(
            session=session,
            model=model,
            left_fk=left_fk,
            right_fk=right_fk,
            left_id=record["id"],
            target_ids=record.get(ids_key, []),
        )
    return total


async def seed_categories_products(session) -> int:
    return await seed_join_table(session, "categories.json", Categories_Product, "categories_id", "product_id", "product_ids")


async def seed_product_links(session) -> dict[str, int]:
    return {
        "product_material": await seed_join_table(session, "product.json", Product_Material, "product_id", "material_id", "material_ids"),
        "product_tag": await seed_join_table(session, "product.json", Product_Tag, "product_id", "tag_id", "tag_ids"),
    }


async def seed_role_permissions(session) -> int:
    return await seed_join_table(session, "role.json", RolePermission, "role_id", "permission_id", "permission_ids")


async def seed_user_roles(session) -> int:
    return await seed_join_table(session, "user.json", UserRole, "user_id", "role_id", "role_ids")


async def seed_all() -> None:
    async with async_session_maker() as session:
        summary: dict[str, Any] = {}

        for file_name in [
            "province.json",
            "ward.json",
            "brand.json",
            "color.json",
            "material.json",
            "permission.json",
            "role.json",
            "special_offer.json",
            "supplier.json",
            "tag.json",
            "warehouse.json",
            "user.json",
            "categories.json",
            "product.json",
            "product_variant.json",
            "address.json",
        ]:
            model = MAIN_MODEL_BY_FILE.get(file_name)
            if model is None:
                continue
            summary[file_name] = await insert_main_table(session, file_name, model)

        summary["categories_product.json"] = {"inserted": await seed_categories_products(session)}
        summary["product_links.json"] = await seed_product_links(session)
        summary["role_permission.json"] = {"inserted": await seed_role_permissions(session)}
        summary["user_role.json"] = {"inserted": await seed_user_roles(session)}

        print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))


def main() -> None:
    asyncio.run(_main())


async def _main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await seed_all()


if __name__ == "__main__":
    main()
