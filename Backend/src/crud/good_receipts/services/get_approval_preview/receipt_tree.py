from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.services.get_approval_preview.data_loader import ApprovalPreviewDataLoaderService
from src.errors.goods_receipt import GoodsReceiptException

data_loader_service = ApprovalPreviewDataLoaderService()

class ReceiptTreeService:
    async def get_all_related_receipts(self, current_gr, po_id: str, session: AsyncSession):
        root_grs = await data_loader_service.load_all_root_receipts(po_id, session)

        if not root_grs:
            return [current_gr]

        all_grs = []
        for root_gr in root_grs:
            tree_grs = await self.build_tree_from_root(root_gr, po_id, session)
            all_grs.extend(tree_grs)

        current_gr_id = str(current_gr.id)
        if not any(str(gr.id) == current_gr_id for gr in all_grs):
            all_grs.append(current_gr)

        return all_grs


    async def build_tree_from_root(self, root_gr, po_id: str, session: AsyncSession) -> List:
        all_grs = [root_gr]
        visited_ids = {str(root_gr.id)}
        current_level = [root_gr]

        while current_level:
            parent_ids = [str(gr.id) for gr in current_level]

            children = await data_loader_service.load_children_receipts_batch(parent_ids, po_id, session)

            if not children:
                break

            next_level = []
            for child in children:
                child_id = str(child.id)

                if child_id in visited_ids:
                    GoodsReceiptException.circular_gr_error()

                visited_ids.add(child_id)
                all_grs.append(child)
                next_level.append(child)

            current_level = next_level

        return all_grs

