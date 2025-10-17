from sqlmodel.ext.asyncio.session import AsyncSession



class ApproveGoodsReceiptService:
    async def approve_goods_receipt(self, session: AsyncSession, goods_receipt_id: str, approved_by: str):
        gr, po, all_related_grs = await self._validate_and_get_data(
            session, goods_receipt_id
        )

    
