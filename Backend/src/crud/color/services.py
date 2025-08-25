from sqlalchemy.orm import noload

from src.crud.color.repositories import ColorRepository
from src.database.models import Color
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, or_
from src.errors.color import ColorException
from src.schemas.color import ColorCreateModel, ColorFilterModel, ColorUpdateModel

color_repository = ColorRepository()

class ColorService:
    async def create_color_service(self, color_data: ColorCreateModel, session: AsyncSession):
        new_color = await color_repository.create_color(color_data, session)

        new_color_dict = {
            "id": str(new_color.id),
            "color": new_color.name,
            "code": new_color.code
        }

        await session.commit()

        return new_color_dict


    async def get_all_color(self, session: AsyncSession, filter_data: ColorFilterModel, skip: int = 0, limit: int = 10):
        conditions = [Color.deleted_at.is_(None)]
        if filter_data.search:
            search_term = f"%{filter_data.search}%"
            conditions.append(or_(
                Color.name.ilike(search_term),
                Color.code.ilike(search_term),
            ))


        joins = [noload(Color.product_variant)]
        colors, total = await color_repository.get_all_color(conditions, session, skip, limit, joins)

        response = []
        for color in colors:
            response.append({
                "id": str(color.id),
                "name": color.name,
                "code": color.code,
            })

        return {
            "data": response,
            "total": total,
        }


    async def update_color_service(self, id: str, color_update: ColorUpdateModel, session: AsyncSession):
        condition = and_(Color.id == id)
        color = await color_repository.get_color(condition, session)

        if not color:
            ColorException.color_not_found()

        update_data = color_update.model_dump(exclude_none=True)

        await color_repository.update_color(color, update_data, session)
        await session.commit()
        await session.refresh(color)

        response_dict = {
            "id": str(color.id),
            "name": color.name,
            "code": color.code
        }

        return response_dict


    async def delete_color(self, color_id: str, session: AsyncSession):
        condition = and_(Color.id == color_id)
        return await color_repository.delete_color(condition, session)