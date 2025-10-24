from src.crud.product.repositories import ProductRepository
from src.crud.user.repositories import UserRepository
from src.crud.notification.services import NotificationService
from src.database.models import Special_Offer, Product, User, UserSpecialOffer
from src.errors.authentication import AuthException
from src.errors.special_offer import SpecialOfferException
from src.errors.user import UserException
from src.schemas.special_offer import SpecialOfferCreateModel, SpecialOfferUpdateModel, SpecialOfferFilterModel, \
    SetOfferToProduct, AssignOfferToUsers
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, or_, select
from src.crud.special_offer.repositories import SpecialOfferRepository
from datetime import datetime
from typing import Any, Optional
from sqlalchemy.orm import noload

special_offer_repository = SpecialOfferRepository()
product_repository = ProductRepository()
user_repository = UserRepository()
notification_service = NotificationService()


class SpecialOfferService:
    async def create_special_offer_service(self, special_offer_data: SpecialOfferCreateModel, session: AsyncSession):
        create_data = special_offer_data.model_dump(exclude_none=True)

        scope = create_data.get("scope", "order")
        condition = create_data.get("condition")

        if scope == "order":
            if condition is not None and condition < 0:
                SpecialOfferException.invalid_condition()
        elif scope == "product":
            create_data["condition"] = None

        if 'start_time' in create_data and 'end_time' in create_data:
            if create_data['end_time'] <= create_data['start_time']:
                SpecialOfferException.end_after_start_time()

        if 'total_quantity' in create_data:
            if create_data['total_quantity'] < 0:
                SpecialOfferException.total_greater_used()

        for k, v in create_data.items():
            if isinstance(v, datetime):
                create_data[k] = v.replace(tzinfo=None)

        new_special_offer = await special_offer_repository.create_special_offer(create_data, session)

        def serialize(obj: Any):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return {k: serialize(v) for k, v in create_data.items()}


    async def get_all_special_offer_service(self, session: AsyncSession, filter_data: SpecialOfferFilterModel, skip: int = 0, limit: int = 10):
        conditions = [Special_Offer.deleted_at.is_(None)]

        if filter_data.search:
            conditions.append(or_(
                Special_Offer.code.ilike(f"%{filter_data.search}%"),
                Special_Offer.name.ilike(f"%{filter_data.search}%")
            ))

        if filter_data.type in ["percent", "fixed"]:
            conditions.append(Special_Offer.type == filter_data.type)

        if filter_data.scope in ["order", "product"]:
            conditions.append(Special_Offer.scope == filter_data.scope)

        if filter_data.discount_min is not None:
            conditions.append(Special_Offer.discount >= filter_data.discount_min)
        if filter_data.discount_max is not None:
            conditions.append(Special_Offer.discount <= filter_data.discount_max)

        if filter_data.quantity_status == "remaining":
            conditions.append(Special_Offer.total_quantity > Special_Offer.used_quantity)
        elif filter_data.quantity_status == "out":
            conditions.append(Special_Offer.total_quantity <= Special_Offer.used_quantity)

        now = datetime.now().replace(microsecond=0)
        if filter_data.time_status == "upcoming":
            conditions.append(Special_Offer.start_time > now)
        elif filter_data.time_status == "active":
            conditions.append(and_(
                Special_Offer.start_time <= now,
                Special_Offer.end_time >= now
            ))
        elif filter_data.time_status == "expired":
            conditions.append(Special_Offer.end_time < now)

        special_offers, total = await special_offer_repository.get_all_special_offer(conditions, session, skip=skip, limit=limit)

        response = []
        for offer in special_offers:
            offer_dict = {
                "id": str(offer.id),
                "code": offer.code,
                "name": offer.name,
                "discount": offer.discount,
                "type": offer.type,
                "scope": offer.scope,
                "condition": offer.condition,
                "total_quantity": offer.total_quantity,
                "used_quantity": offer.used_quantity,
                "start_time": str(offer.start_time),
                "end_time": str(offer.end_time),
            }
            response.append(offer_dict)

        return {
            "data": response,
            "total": total
        }


    async def get_all_special_offer_customer_service(self, user_id: str, session: AsyncSession, search: Optional[str], skip: int = 0, limit: int = 10):
        condition_offers = [Special_Offer.deleted_at.is_(None), Special_Offer.scope == 'order',
                            Special_Offer.start_time <= datetime.now(), Special_Offer.end_time >= datetime.now(),
                            Special_Offer.total_quantity > Special_Offer.used_quantity]

        if search:
            search_term = f"%{search}%"
            condition_offers.append(or_(
                Special_Offer.name.ilike(search_term),
                Special_Offer.code.ilike(search_term),
            ))

        subquery = (
            select(UserSpecialOffer.special_offer_id)
            .where(UserSpecialOffer.user_id == user_id)
        )

        condition_offers.append(Special_Offer.id.in_(subquery))

        special_offers, total = await special_offer_repository.get_all_special_offer(condition_offers, session, skip, limit)

        response = []
        for offer in special_offers:
            offer_dict = {
                "id": str(offer.id),
                "code": offer.code,
                "name": offer.name,
                "discount": offer.discount,
                "type": offer.type,
                "scope": offer.scope,
                "condition": offer.condition,
                "total_quantity": offer.total_quantity,
                "used_quantity": offer.used_quantity,
                "start_time": str(offer.start_time),
                "end_time": str(offer.end_time),
            }
            response.append(offer_dict)

        return {
            "data": response,
            "total": total
        }

    async def update_special_offer_service(self, id: str, special_offer_update: SpecialOfferUpdateModel,
                                           session: AsyncSession):
        condition = and_(Special_Offer.id == id)
        special_offer = await special_offer_repository.get_special_offer(condition, session)

        if not special_offer:
            SpecialOfferException.not_found()

        update_data = special_offer_update.model_dump(exclude_none=True)

        if special_offer.used_quantity > 0:
            allowed_fields = {'name', 'end_time'}
            not_allowed_fields = set(update_data.keys()) - allowed_fields
            if not_allowed_fields:
                SpecialOfferException.not_update_fields()

        if 'start_time' in update_data and 'end_time' in update_data:
            if update_data['end_time'] <= update_data['start_time']:
                SpecialOfferException.end_after_start_time()
        elif 'end_time' in update_data:
            if update_data['end_time'] <= special_offer.start_time:
                SpecialOfferException.end_after_start_time()
        elif 'start_time' in update_data:
            if special_offer.end_time <= update_data['start_time']:
                SpecialOfferException.end_after_start_time()

        if 'total_quantity' in update_data:
            if update_data['total_quantity'] < special_offer.used_quantity:
                SpecialOfferException.total_greater_used()

        new_scope = update_data.get("scope")
        old_scope = special_offer.scope

        if new_scope:
            if old_scope == "order" and new_scope == "product":
                update_data["condition"] = None
                special_offer.condition = None
            elif old_scope == "product" and new_scope == "order":
                if "condition" not in update_data:
                    update_data["condition"] = special_offer.condition
        else:
            if "condition" not in update_data:
                update_data["condition"] = special_offer.condition

        for k, v in update_data.items():
            if isinstance(v, datetime):
                update_data[k] = v.replace(tzinfo=None)

        await special_offer_repository.update_special_offer(special_offer, update_data, session)

        def serialize(obj: Any):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return {k: serialize(v) for k, v in update_data.items()}

    async def delete_categories_service(self, id: str, session: AsyncSession):
        condition = and_(Special_Offer.id == id)
        return await special_offer_repository.delete_special_offer(condition, session)


    async def set_offer_to_product_service(self, data: SetOfferToProduct, session: AsyncSession):
        condition_offer = and_(Special_Offer.id == data.special_offer_id, Special_Offer.deleted_at.is_(None))
        special_offer = await special_offer_repository.get_special_offer(condition_offer, session)
        if not special_offer:
            SpecialOfferException.not_found()

        if special_offer.scope != "product":
            SpecialOfferException.invalid_scope_for_product()

        now = datetime.utcnow()
        if not (special_offer.start_time <= now <= special_offer.end_time):
            SpecialOfferException.expired_or_not_started()

        if special_offer.used_quantity >= special_offer.total_quantity:
            SpecialOfferException.insufficient_quantity()

        condition_product = Product.id.in_(data.product_id)
        await product_repository.update_product_some_field(
            condition_product,
            {"special_offer_id": data.special_offer_id},
            session
        )

    async def assign_offer_to_users_service(self, data: AssignOfferToUsers, session: AsyncSession):
        condition_offer = and_(Special_Offer.id == data.special_offer_id, Special_Offer.deleted_at.is_(None))
        special_offer = await special_offer_repository.get_special_offer(condition_offer, session)
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








