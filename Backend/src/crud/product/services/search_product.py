import re
from typing import Dict, Any, List, Tuple
from sqlalchemy import exists
from sqlalchemy.orm import selectinload
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.utils import UtilProductsService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories, Product_Variant, Special_Offer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, or_
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
utils_service = UtilProductsService()


class SearchProductService:
    PRODUCT_KEYWORDS = [
        'hình', 'phong cách', 'màu', 'size', 'cỡ', 'kiểu', 'form', 'dáng', 
        'đồ', 'quần áo', 'giày', 'túi', 'phụ kiện', 'áo', 'quần', 'váy',
        'đầm', 'jacket', 'hoodie', 'sweater', 'jean', 'kaki'
    ]
    
    MAX_CATEGORY_RESULTS = 10
    MAX_PRODUCT_RESULTS = 50
    
    async def search_product(self, search: str, session: AsyncSession, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        search_normalized = await self.normalize_search_query(search)
        
        if not search_normalized:
            return {
                "categories": [],
                "products": [],
                "total_categories": 0,
                "total_products": 0,
                "search_type": "invalid",
                "search_info": {
                    "original_search": search,
                    "normalized_search": "",
                    "has_results": False
                }
            }
        
        search_words = search_normalized.split()

        results = {
            "categories": [],
            "products": [],
            "total_categories": 0,
            "total_products": 0,
            "search_type": await self.determine_search_type(search_normalized),
            "search_info": {
                "original_search": search,
                "normalized_search": search_normalized,
                "word_count": len(search_words),
                "has_parent_from_child": False,
                "has_results": False
            }
        }

        await self.search_categories(search_normalized, results, session)

        should_search_prods = await self.should_search_products(search_normalized, search_words)
        
        if should_search_prods:
            await self.search_products(search_normalized, results, session, skip, limit)

        results["search_info"]["has_parent_from_child"] = any(
            cat.get("type") == "parent_from_child_match"
            for cat in results["categories"]
        )
        results["search_info"]["has_results"] = (
            len(results["categories"]) > 0 or len(results["products"]) > 0
        )

        return results
    
    
    async def normalize_search_query(self, search: str) -> str:
        if not search:
            return ""
        
        search = search.strip().lower()
        search = re.sub(
            r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', 
            '', 
            search
        )
        search = re.sub(r'\s+', ' ', search).strip()
        return search
    
    
    async def determine_search_type(self, search: str) -> str:
        if not search:
            return "invalid"
        
        words = search.split()
        word_count = len(words)
        char_count = len(search)

        if word_count == 1 and char_count <= 4:
            return "category_focused"
        elif word_count >= 3 or char_count >= 15:
            return "product_focused"
        else:
            return "mixed"
        
        
    async def search_categories(self, search: str, results: Dict[str, Any], session: AsyncSession):
        if not search:
            return
        
        condition = [
            Categories.name.ilike(f"%{search}%"),
            Categories.deleted_at.is_(None)
        ]
        
        options = [
            selectinload(Categories.children).load_only(
                Categories.id,
                Categories.name,
                Categories.slug,
                Categories.deleted_at
            ),
            selectinload(Categories.parent).load_only(
                Categories.id,
                Categories.name,
                Categories.slug,
                Categories.deleted_at
            )
        ]
        
        categories, total = await categories_repository.get_all_categories(session=session, where_conditions=condition, options=options,
                                                                       skip=0, limit=self.MAX_CATEGORY_RESULTS)
        
        results["total_categories"] = total

        added_parents = {}
        for cat in categories:
            if cat.parent_id is None:
                parent_data = self.build_parent_category_data(
                    cat, 
                    "parent_direct_match",
                    []
                )
                added_parents[str(cat.id)] = parent_data
                results["categories"].append(parent_data)

            elif cat.parent and cat.parent.deleted_at is None:
                parent_id = str(cat.parent.id)

                if parent_id not in added_parents:
                    condition = [
                        Categories.parent_id == cat.parent.id,
                        Categories.deleted_at.is_(None)
                    ]
                    parent_children, _ = await categories_repository.get_all_categories(
                        session=session,
                        where_conditions=condition,
                        skip=0,
                        limit=100
                    )
                    
                    parent_data = self.build_parent_category_data(
                        cat.parent,
                        "parent_from_child_match",
                        [cat.name],
                        parent_children
                    )

                    added_parents[parent_id] = parent_data
                    results["categories"].append(parent_data)
                else:
                    if cat.name not in added_parents[parent_id]["matched_children"]:
                        added_parents[parent_id]["matched_children"].append(cat.name)
                        
                        
    def build_parent_category_data(self, category: Categories, match_type: str, matched_children: List[str], 
                                    children_list: List[Categories] = None) -> Dict[str, Any]:
        
        children = children_list if children_list is not None else category.children
        
        active_children = [
            {
                "id": str(c.id),
                "name": c.name,
                "slug": c.slug if hasattr(c, 'slug') else None
            }
            for c in children
            if c.deleted_at is None
        ]
        
        return {
            "id": str(category.id),
            "name": category.name,
            "slug": category.slug if hasattr(category, 'slug') else None,
            "type": match_type,
            "children": active_children,
            "children_count": len(active_children),
            "matched_children": matched_children
        }
        
        
    async def should_search_products(self, search: str, search_words: List[str]) -> bool:
        if not search or not search_words:
            return False

        if len(search_words) >= 2 or len(search) >= 3:
            return True

        if any(keyword in search for keyword in self.PRODUCT_KEYWORDS):
            return True

        return False
        

    async def search_products(self, search: str, results: Dict[str, Any], session: AsyncSession, 
                              skip: int, limit: int):
        if not search:
            return
        
        search_words = search.split()

        conditions = [
            Product.deleted_at.is_(None),
            Product.status == "active",
            exists().where(
                and_(
                    Product_Variant.product_id == Product.id,
                    Product_Variant.deleted_at.is_(None),
                    Product_Variant.quantity > 0
                )
            )
        ]

        name_conditions = []
        name_conditions.append(Product.name.ilike(f"%{search}%"))
        
        for word in search_words:
            if len(word) >= 2:
                name_conditions.append(Product.name.ilike(f"%{word}%"))

        conditions.append(or_(*name_conditions))

        options = [
            selectinload(Product.categories).load_only(
                Categories.id,
                Categories.name,
                Categories.slug,
                Categories.deleted_at
            ),
            selectinload(Product.product_variant).load_only(
                Product_Variant.id,
                Product_Variant.price,
                Product_Variant.quantity,
                Product_Variant.deleted_at
            ),
            selectinload(Product.special_offer).load_only(
                Special_Offer.id,
                Special_Offer.discount,
                Special_Offer.type,
                Special_Offer.used_quantity,
                Special_Offer.total_quantity,
                Special_Offer.start_time,
                Special_Offer.end_time,
                Special_Offer.deleted_at
            )
        ]

        products, total = await product_repository.get_all_product(
            session=session,
            where_conditions=conditions,
            options=options,
            skip=0,
            limit=min(self.MAX_PRODUCT_RESULTS, limit * 3)
        )
        results["total_products"] = total

        valid_products = []
        for product_tuple in products:
            product = product_tuple[0]
            
            active_variants = [
                variant for variant in product.product_variant
                if variant.deleted_at is None and variant.quantity > 0
            ]
            
            if active_variants:
                valid_products.append((product, active_variants))

        ranked_products = await self.rank_products(valid_products, search, search_words)
        
        paginated = ranked_products[skip:skip + limit]

        for product, variants, score in paginated:
            product_data = await self.build_product_search_result(
                product, variants, score
            )
            results["products"].append(product_data)
            
            
    async def build_product_search_result(self, product: Product, active_variants: List[Product_Variant],
                                          relevance_score: float) -> Dict[str, Any]:
        prices = [v.price for v in active_variants if v.price is not None]
        price_min = min(prices) if prices else 0

        offer = product.special_offer
        offer_status = utils_service.get_offer_status(offer)
        
        original_price = price_min
        discounted_price = original_price

        if offer_status["is_valid"] and offer:
            if offer.type == "percent":
                raw_discounted = original_price * (1 - offer.discount / 100)
                discounted_price = int(round(raw_discounted / 1000) * 1000)
            elif offer.type == "fixed":
                raw_discounted = max(0, original_price - offer.discount)
                discounted_price = int(round(raw_discounted / 1000) * 1000)

        product_data = {
            "id": str(product.id),
            "name": product.name,
            "slug": product.slug,
            "images": product.images[:2] if product.images else [],
            "original_price": original_price,
            "discounted_price": discounted_price,
            "avg_rating": float(product.avg_rating) if product.avg_rating else 0.0,
            "total_sold": product.total_sold if product.total_sold else 0,
            "relevance_score": round(relevance_score, 2)
        }

        valid_categories = [
            cat for cat in product.categories 
            if cat.deleted_at is None
        ]
        
        if valid_categories:
            first_cat = valid_categories[0]
            product_data["category"] = {
                "id": str(first_cat.id),
                "name": first_cat.name,
                "slug": first_cat.slug if hasattr(first_cat, 'slug') else None
            }

        return product_data
    
    
    async def rank_products(self, products_with_variants: List[Tuple[Product, List[Product_Variant]]],
                            search: str, search_words: List[str]):
        ranked = []
        search_lower = search.lower()

        for product, variants in products_with_variants:
            product_name_lower = product.name.lower()
            score = 0.0

            if search_lower == product_name_lower:
                score += 100

            elif search_lower in product_name_lower:
                score += 50
                
                if product_name_lower.startswith(search_lower):
                    score += 20

            for word in search_words:
                word_lower = word.lower()
                if word_lower in product_name_lower:
                    score += 10
                    
                    if product_name_lower.startswith(word_lower):
                        score += 5
                        
            score -= len(product.name) * 0.1

            if product.total_sold:
                score += min(product.total_sold * 0.01, 10)
            
            if product.avg_rating:
                score += product.avg_rating * 2

            ranked.append((product, variants, score))

        return sorted(ranked, key=lambda x: x[2], reverse=True)

