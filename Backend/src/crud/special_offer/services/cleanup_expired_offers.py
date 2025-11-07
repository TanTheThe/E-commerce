from datetime import datetime
from src.database.models import Product, Special_Offer
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.product.repositories import ProductRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
import logging

special_offer_repository = SpecialOfferRepository()
product_repository = ProductRepository()

logger = logging.getLogger(__name__)

class OfferCleanupService:
    async def cleanup_expired_offers(self, session: AsyncSession):
        try:
            select_columns = [Product, Special_Offer]

            joins = [
                (Product, {"type": "inner", "on": (Product.special_offer_id == Special_Offer.id)})
            ]

            where_conditions = [
                Product.deleted_at.is_(None),
                Product.special_offer_id.isnot(None),
                Special_Offer.deleted_at.is_(None),
                Special_Offer.end_time < datetime.now()
            ]

            products_with_expired_offers, total = await special_offer_repository.get_all_special_offer(
                session=session, select_columns=select_columns,
                joins=joins, where_conditions=where_conditions,
                limit=1000
            )

            if not products_with_expired_offers:
                logger.info("No expired offers found")
                return {
                    'success': True,
                    'count': 0,
                    'product_ids': [],
                    'message': 'No expired offers to cleanup'
                }

            product_ids = []
            offer_info = {}

            for product, offer in products_with_expired_offers:
                product_ids.append(product.id)
                if offer.id not in offer_info:
                    offer_info[offer.id] = {
                        'code': offer.code,
                        'name': offer.name,
                        'end_time': offer.end_time,
                        'product_count': 0
                    }
                offer_info[offer.id]['product_count'] += 1

            condition_update = and_(Product.id.in_(product_ids))

            update_dict = {
                "special_offer_id": None,
                "updated_at": datetime.now()
            }

            await product_repository.update_product_some_field(condition_update, update_dict, session)

            await session.commit()

            return {
                'product_ids': [str(pid) for pid in product_ids],
                'offers_cleaned': [
                    {
                        'offer_code': info['code'],
                        'offer_name': info['name'],
                        'expired_at': info['end_time'].isoformat(),
                        'products_affected': info['product_count']
                    }
                    for info in offer_info.values()
                ]
            }

        except Exception as e:
            logger.error(f"Error cleaning up expired offers: {str(e)}")
            await session.rollback()
            raise



