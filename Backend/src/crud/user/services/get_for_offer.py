from typing import Optional
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import User, UserSpecialOffer
from sqlmodel import or_, func, desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.user.repositories import UserRepository

user_repository = UserRepository()
warehouse_repository = WareHouseRepository()


class GetAllCustomerForOfferService:
    async def get_all_customer_for_offer(self, offer_id: str, search: Optional[str], session: AsyncSession,
                                                 skip: int = 0, limit: int = 10):
        filters = [
            User.deleted_at.is_(None),
            User.is_customer == True,
            User.customer_status == "active",
            User.is_verified == True
        ]

        if search:
            search = search.strip()
            if search:
                search_term = f"%{search}%"
                filters.append(or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                    func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
                ))

        subquery = (
            select(UserSpecialOffer.user_id)
            .where(
                UserSpecialOffer.special_offer_id == offer_id,
            )
            .scalar_subquery()
        )
        filters.append(~User.id.in_(subquery))

        order_by = desc(User.created_at)

        users, total = await user_repository.get_all_users(session=session, where_conditions=filters, skip=skip,
                                                           limit=limit, order_by=order_by)

        filtered_users = [
            {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "customer_status": user.customer_status,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ]

        return {
            "data": filtered_users,
            "total": total
        }


