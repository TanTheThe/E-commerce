from src.crud.color.repositories import ColorRepository
from src.database.models import Color
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import or_
from src.errors.color import ColorException
from src.schemas.color import ColorCreateModel, ColorFilterModel, ColorUpdateModel

color_repository = ColorRepository()

class ColorService:
    async def create_color_service(self, color_data: ColorCreateModel, session: AsyncSession):
        condition_name = [Color.name == color_data.name, Color.deleted_at.is_(None)]
        existing = await color_repository.get_color(
            session=session,
            where_conditions=condition_name,
        )
        if existing:
            ColorException.name_already_exists()

        condition_code = [Color.code == color_data.code, Color.deleted_at.is_(None)]
        existing_code = await color_repository.get_color(
            session=session,
            where_conditions=condition_code,
        )
        if existing_code:
            ColorException.code_already_exists()

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

        colors, total = await color_repository.get_all_color(session=session, where_conditions=conditions, skip=skip, limit=limit)

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
        condition = [Color.id == id, Color.deleted_at.is_(None)]
        color = await color_repository.get_color(session=session, where_conditions=condition)

        if not color:
            ColorException.color_not_found()

        update_data = color_update.model_dump(exclude_none=True)

        if 'name' in update_data:
            condition = [
                Color.name == update_data['name'],
                Color.id != id,
                Color.deleted_at.is_(None)
            ]
            existing = await color_repository.get_color(session, where_conditions=condition)

            if existing:
                ColorException.name_already_exists()

        if 'code' in update_data:
            condition = [
                Color.code == update_data['code'],
                Color.id != id,
                Color.deleted_at.is_(None)
            ]
            existing_code = await color_repository.get_color(session, where_conditions=condition)
            if existing_code:
                ColorException.code_already_exists()

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
        condition = [Color.id == color_id, Color.deleted_at.is_(None)]
        return await color_repository.delete_color(condition, session)