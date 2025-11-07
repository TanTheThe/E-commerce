from src.database.models import Special_Offer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.crud.special_offer.repositories import SpecialOfferRepository

special_offer_repository = SpecialOfferRepository()


class DeleteSpecialOfferService:
    async def delete_special_offer(self, id: str, session: AsyncSession):
        condition = and_(Special_Offer.id == id)
        return await special_offer_repository.delete_special_offer(condition, session)











