from typing import List
import uuid
from src.celery_tasks.send_assign_offer_notification import send_assign_offer_notifications_task
from src.crud.product.repositories import ProductRepository
from src.crud.user.repositories import UserRepository
from src.database.models import Special_Offer, User, UserSpecialOffer
from src.errors.special_offer import SpecialOfferException
from src.schemas.special_offer import AssignOfferToUsers
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.special_offer.repositories import SpecialOfferRepository
from datetime import datetime

special_offer_repository = SpecialOfferRepository()
product_repository = ProductRepository()
user_repository = UserRepository()


class AssignOfferToUsersService:
    async def assign_offer_to_users(self, data: AssignOfferToUsers, session: AsyncSession):
        special_offer = await self.validate_and_lock_special_offer(data.special_offer_id, session)

        user_validation = await self.validate_users(data.user_ids, session)

        if len(user_validation['valid_users']) == 0:
            SpecialOfferException.no_valid_user_to_assign()

        assignment_check = await self.check_existing_assignments(
            special_offer_id=data.special_offer_id,
            user_ids=user_validation['valid_users'],
            session=session
        )

        users_to_assign = assignment_check['new_users']

        if len(users_to_assign) == 0:
            SpecialOfferException.all_users_already_assigned()

        required_quantity = len(users_to_assign)
        available_quantity = special_offer.total_quantity - special_offer.used_quantity

        if required_quantity > available_quantity:
            SpecialOfferException.insufficient_number_of_offers(required_quantity, available_quantity)

        await self.bulk_create_assignments(
            special_offer_id=data.special_offer_id,
            user_ids=users_to_assign,
            session=session
        )

        if data.send_notification and users_to_assign:
            send_assign_offer_notifications_task.apply_async(
                args=[
                    str(data.special_offer_id),
                    special_offer.name,
                    [str(uid) for uid in users_to_assign],
                    data.admin_note
                ],
                countdown=5
            )

        await session.commit()

        return {
            "special_offer_id": str(data.special_offer_id),
            "special_offer_code": special_offer.code,
            "special_offer_name": special_offer.name,
            "total_requested": len(data.user_ids),
            "successfully_assigned": len(users_to_assign),
            "already_assigned": len(assignment_check['already_assigned']),
            "invalid_users": len(user_validation['invalid_users']),
            "assigned_user_ids": [str(uid) for uid in users_to_assign],
            "skipped_user_ids": [str(uid) for uid in assignment_check['already_assigned']],
            "invalid_user_ids": [str(uid) for uid in user_validation['invalid_users']]
        }


    async def validate_and_lock_special_offer(self, offer_id: str, session: AsyncSession):
        conditions = [
            Special_Offer.id == offer_id,
            Special_Offer.deleted_at.is_(None)
        ]

        special_offer = await special_offer_repository.get_special_offer(session=session, where_conditions=conditions,
                                                                         for_update=True)

        if not special_offer:
            SpecialOfferException.not_found()

        if special_offer.scope != "order":
            SpecialOfferException.invalid_scope_for_order(special_offer)

        now = datetime.now().replace(microsecond=0)
        if now < special_offer.start_time:
            SpecialOfferException.offer_not_started_yet()

        if now > special_offer.end_time:
            SpecialOfferException.offer_has_expired()

        if special_offer.used_quantity >= special_offer.total_quantity:
            SpecialOfferException.insufficient_quantity()

        return special_offer


    async def validate_users(self, user_ids: List[str], session: AsyncSession):
        conditions = [
            User.id.in_(user_ids),
            User.deleted_at.is_(None),
            User.customer_status == 'active'
        ]

        users, _ = user_repository.get_all_users(session=session, where_conditions=conditions)

        valid_user_ids = [str(row.id) for row in users]
        valid_set = set(valid_user_ids)
        invalid_user_ids = [uid for uid in user_ids if uid not in valid_set]

        return {
            'valid_users': valid_user_ids,
            'invalid_users': invalid_user_ids
        }


    async def check_existing_assignments(self, special_offer_id: str, user_ids: List[str], session: AsyncSession):
        conditions = [
            UserSpecialOffer.special_offer_id == special_offer_id,
            UserSpecialOffer.user_id.in_(user_ids)
        ]

        user_offers, _ = await special_offer_repository.get_all_user_special_offer(session=session, where_conditions=conditions)

        already_assigned = [str(row.user_id) for row in user_offers]
        already_assigned_set = set(already_assigned)

        new_users = [uid for uid in user_ids if uid not in already_assigned_set]

        return {
            'new_users': new_users,
            'already_assigned': already_assigned
        }


    async def bulk_create_assignments(self, special_offer_id: str, user_ids: List[str], session: AsyncSession):
        if not user_ids:
            return

        assignments = [
            {
                'id': uuid.uuid4(),
                'special_offer_id': special_offer_id,
                'user_id': user_id,
                'used_at': None
            }
            for user_id in user_ids
        ]

        await special_offer_repository.bulk_create_assignments(session=session, assignments=assignments)



