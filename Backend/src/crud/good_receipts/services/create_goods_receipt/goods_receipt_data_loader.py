from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import GoodsReceipt, Product_Variant
from sqlalchemy.orm import selectinload

product_variant_repository = ProductVariantRepository()
goods_receipt_repository = GoodsReceiptRepository()

class GoodsReceiptDataLoaderService:
    async def batch_load_variants(self, variant_ids: List[str], session: AsyncSession):
        conditions = [Product_Variant.id.in_(variant_ids)]
        options = [
            selectinload(Product_Variant.product),
            selectinload(Product_Variant.color)
        ]
        
        variants, _ = await product_variant_repository.get_all_product_variant(
            session=session,
            where_conditions=conditions,
            options=options
        )

        return {str(v.id): v for v in variants}
    
    
    async def batch_load_sibling_receipts(self, parent_receipt_id: str, session: AsyncSession) -> List:
        child_condition = [GoodsReceipt.parent_receipt_id == parent_receipt_id]
        child_options = [selectinload(GoodsReceipt.receipt_details)]
        
        sibling_grs, _ = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=child_condition,
            options=child_options
        )
        return sibling_grs