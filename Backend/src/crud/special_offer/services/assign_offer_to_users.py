from src.crud.product.repositories import ProductRepository
from src.crud.user.repositories import UserRepository
from src.crud.notification.services import NotificationService
from src.database.models import Special_Offer, User, UserSpecialOffer
from src.errors.authentication import AuthException
from src.errors.special_offer import SpecialOfferException
from src.schemas.special_offer import AssignOfferToUsers
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.special_offer.repositories import SpecialOfferRepository
from datetime import datetime

special_offer_repository = SpecialOfferRepository()
product_repository = ProductRepository()
user_repository = UserRepository()
notification_service = NotificationService()


class AssignOfferToUsersService:
    async def assign_offer_to_users(self, data: AssignOfferToUsers, session: AsyncSession):
        condition_offer = [Special_Offer.id == data.special_offer_id, Special_Offer.deleted_at.is_(None)]
        special_offer = await special_offer_repository.get_special_offer(session=session, where_conditions=condition_offer)
        if not special_offer:
            SpecialOfferException.not_found()

        if special_offer.scope != "order":
            SpecialOfferException.invalid_scope_for_product()

        now = datetime.utcnow()
        if not (special_offer.start_time <= now <= special_offer.end_time):
            SpecialOfferException.expired_or_not_started()

        condition_user = [User.id.in_(data.user_ids), User.deleted_at.is_(None), User.customer_status == 'active']
        existing_users, _ = await user_repository.get_all_users(condition_user, session, 0, 1000)
        existing_user_ids = {user.id for user in existing_users}

        missing_user_ids = set(data.user_ids) - existing_user_ids
        if missing_user_ids:
            AuthException.user_not_found()

        condition = [
            UserSpecialOffer.special_offer_id == data.special_offer_id,
            UserSpecialOffer.user_id.in_(list(existing_user_ids))
        ]
        existing_assignments = await special_offer_repository.get_all_user_special_offer(condition, session=session)
        already_assigned_user_ids = {assignment.user_id for assignment in existing_assignments}
        if already_assigned_user_ids:
            SpecialOfferException.exists_user_special_offer()

        user_offers = [
            UserSpecialOffer(
                special_offer_id=data.special_offer_id,
                user_id=user_id,
            )
            for user_id in existing_user_ids
        ]
        await special_offer_repository.bulk_create_user_special_offer(user_offers, session=session)

        for user_id in existing_user_ids:
            await notification_service.create_assign_special_offer_notification(
                session=session,
                special_offer_id=str(data.special_offer_id),
                special_offer_name=special_offer.name,
                customer_id=str(user_id),
                admin_note=data.admin_note  # Nếu có admin_note trong data
            )

        await session.commit()

        return {
            "special_offer_id": str(data.special_offer_id),
            "user_ids": list(str(existing_user_ids))
        }











