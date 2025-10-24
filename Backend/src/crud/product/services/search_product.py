import re
from typing import Dict, Any, List
from sqlalchemy.orm import selectinload
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories, Product_Variant
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import or_
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService

product_repository = ProductRepository()
categories_repository = CategoriesRepository()
cate_product_repository = CategoriesProductRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
size_repository = SizeRepository()

product_variant_service = ProductVariantService()
categories_product_service = CategoriesProductService()
color_service = ColorService()


class SearchProductService:
    async def normalize_search_query(self, search: str) -> str:
        search = re.sub(r'\s+', ' ', search.strip().lower())
        search = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', '', search)
        return search

    async def determine_search_type(self, search: str) -> str:
        words = search.split()

        if len(words) == 1 and len(search) <= 4:
            return "category_focused"
        elif len(words) >= 3 or len(search) >= 10:
            return "product_focused"
        else:
            return "mixed"

    async def search_categories(self, search: str, results: Dict[str, Any], session: AsyncSession):
        condition_search_categories = [Categories.name.ilike(f"%{search}%"), Categories.deleted_at.is_(None)]
        joins_search_categories = [
            selectinload(Categories.children),
            selectinload(Categories.parent)
        ]
        categories, _ = await categories_repository.get_all_categories(session=session, where_conditions=condition_search_categories,
                                                                       options=joins_search_categories)
        added_categories = {}
        for cat in categories:
            if cat.parent_id is None:
                active_children = [
                    {"id": str(c.id), "name": c.name}
                    for c in cat.children
                    if c.deleted_at is None
                ]

                parent_data = {
                    "id": str(cat.id),
                    "name": cat.name,
                    "type": "parent_direct_match",
                    "children": active_children,
                    "children_count": len(active_children),
                    "matched_children": []
                }
                added_categories[str(cat.id)] = parent_data
                results["categories"].append(parent_data)

            elif cat.parent and cat.parent.deleted_at is None:
                parent_id = str(cat.parent.id)

                if parent_id not in added_categories:
                    condition_parent = [
                        Categories.parent_id == cat.parent.id,
                        Categories.deleted_at.is_(None)
                    ]
                    parent_children, _ = await categories_repository.get_all_categories(session=session, where_conditions=condition_parent)
                    active_children = [
                        {"id": str(c.id), "name": c.name}
                        for c in parent_children
                        if c.deleted_at is None
                    ]

                    parent_data = {
                        "id": parent_id,
                        "name": cat.parent.name,
                        "type": "parent_from_child_match",
                        "children": active_children,
                        "children_count": len(active_children),
                        "matched_children": [cat.name]
                    }
                    added_categories[parent_id] = parent_data
                    results["categories"].append(parent_data)
                else:
                    added_categories[parent_id]["matched_children"].append(cat.name)

    async def should_search_products(self, search: str, search_words: List[str]) -> bool:
        product_keywords = ['hình', 'phong cách', 'màu', 'size', 'cỡ', 'kiểu', 'form', 'dáng', 'đồ', 'quần áo', 'giày',
                            'túi', 'phụ kiện']

        return (
                len(search_words) >= 2 or
                len(search) >= 3 or
                any(keyword in search for keyword in product_keywords)
        )

    async def search_products(self, search: str, results: Dict[str, Any], session: AsyncSession, skip: int, limit: int):
        search_words = search.split()

        conditions = [
            Product.deleted_at.is_(None),
            Product.status == "active"
        ]

        name_conditions = []
        for word in search_words:
            name_conditions.append(Product.name.ilike(f"%{word}%"))

        name_conditions.append(Product.name.ilike(f"%{search}%"))
        conditions.append(or_(*name_conditions))

        joins_products = [
            selectinload(Product.categories),
            selectinload(Product.product_variant).load_only(
                Product_Variant.id,
                Product_Variant.quantity,
                Product_Variant.deleted_at
            )
        ]

        products, _ = await product_repository.get_all_product(
            conditions,
            session,
            joins=joins_products,
            skip=skip,
            limit=limit
        )

        valid_products = []
        for product_tuple in products:
            product = product_tuple[0]
            active_variants = [
                variant for variant in product.product_variant
                if variant.deleted_at is None and variant.quantity > 0
            ]
            if active_variants:
                valid_products.append(product)

        ranked_products = await self.rank_products(products, search, search_words)

        for product, score in ranked_products[:limit]:
            product_data = {
                "id": str(product.id),
                "name": product.name,
                "relevance_score": score
            }

            if product.categories:
                first_category = product.categories[0]
                product_data["category"] = {
                    "id": str(first_category.id),
                    "name": first_category.name
                }

            results["products"].append(product_data)

    async def rank_products(self, products: List, search: str, search_words: List[str]) -> List[tuple]:
        ranked = []
        search_lower = search.lower()

        for product in products:
            product = product[0]
            product_name_lower = product.name.lower()
            score = 0

            if search_lower == product_name_lower:
                score += 100

            elif search_lower in product_name_lower:
                score += 50
                if product_name_lower.startswith(search_lower):
                    score += 20

            for word in search_words:
                if word.lower() in product_name_lower:
                    score += 10
                    if product_name_lower.startswith(word.lower()):
                        score += 5

            score -= len(product.name) * 0.1

            ranked.append((product, score))

        return sorted(ranked, key=lambda x: x[1], reverse=True)

    async def search_product(self, search: str, session: AsyncSession, skip: int = 0, limit: int = 10):
        search_normalized = await self.normalize_search_query(search)
        search_words = search_normalized.split()

        results = {
            "categories": [],
            "products": [],
            "search_type": await self.determine_search_type(search_normalized),
            "search_info": {
                "original_search": search,
                "normalized_search": search_normalized,
                "has_parent_from_child": False
            }
        }

        await self.search_categories(search_normalized, results, session)

        results["search_info"]["has_parent_from_child"] = any(
            cat.get("type") == "parent_from_child_match"
            for cat in results["categories"]
        )

        should_search_products = await self.should_search_products(search_normalized, search_words)
        if should_search_products:
            await self.search_products(search_normalized, results, session, skip, limit)

        return results
