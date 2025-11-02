from datetime import datetime
from sqlalchemy import update, delete
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product.repositories import ProductRepository
from src.crud.supplier.repositories import SupplierRepository
from src.database.models import Supplier, Product, Supplier_Product
from src.errors.product import ProductException
from src.errors.supplier import SupplierException
from src.schemas.supplier import SupplierUpdate

supplier_repository = SupplierRepository()
product_repository = ProductRepository()


class UpdateSupplierService:
    async def update_supplier(self, supplier_id: str, supplier_data: SupplierUpdate, session: AsyncSession):
        condition = [Supplier.id == supplier_id]
        existing = await supplier_repository.get_supplier(session=session, where_conditions=condition)
        if not existing:
            SupplierException.supplier_not_found()

        if supplier_data.credit_limit is not None and supplier_data.credit_limit < 0:
            SupplierException.credit_cant_negative()

        update_data = supplier_data.model_dump(exclude_unset=True, exclude={'add_products', 'remove_product_ids', 'update_products'})

        if update_data:
            update_data['updated_at'] = datetime.now()
            await supplier_repository.update_supplier(and_(*condition), update_data, session)

        if supplier_data.add_products:
            product_ids = [item.product_id for item in supplier_data.add_products]

            product_checks, _ = await product_repository.get_all_product(session=session, where_conditions=[Product.id.in_(product_ids)])
            existing_product_ids = {str(row[0].id) for row in product_checks}

            missing_products = set(product_ids) - existing_product_ids
            if missing_products:
                ProductException.some_products_not_exists()

            existing_links_result, _ = await supplier_repository.get_all_suppliers_product(
                session=session,
                where_conditions=[Supplier_Product.supplier_id == supplier_id,
                                  Supplier_Product.product_id.in_(product_ids)]
            )

            existing_links = {str(row.product_id): str(row.id) for row in existing_links_result}

            updates = []
            items_to_create = []

            item_dict = {item.product_id: item for item in supplier_data.add_products}

            for product_id in product_ids:
                item = item_dict[product_id]

                if product_id in existing_links:
                    updates.append({
                        "id": existing_links[product_id],
                        "is_active": item.is_active,
                        "notes": item.notes,
                        "updated_at": datetime.now()
                    })
                else:
                    items_to_create.append({
                        'supplier_id': supplier_id,
                        'product_id': product_id,
                        'is_active': item.is_active,
                        'notes': item.notes,
                        'created_at': datetime.now()
                    })

            if updates:
                statement = update(Supplier_Product)
                await session.execute(statement, updates)

            if items_to_create:
                session.add_all([
                    Supplier_Product(**item_data)
                    for item_data in items_to_create
                ])

        if supplier_data.remove_product_ids:
            delete_stmt = delete(Supplier_Product).where(
                and_(
                    Supplier_Product.supplier_id == supplier_id,
                    Supplier_Product.product_id.in_(supplier_data.remove_product_ids)
                )
            )

            await session.execute(delete_stmt)

        if supplier_data.update_products:
            product_ids = [item.product_id for item in supplier_data.update_products]

            existing_links_result, _ = await supplier_repository.get_all_suppliers_product(
                session=session,
                where_conditions=[Supplier_Product.supplier_id == supplier_id,
                                  Supplier_Product.product_id.in_(product_ids)]
            )

            existing_links = {str(row.product_id): str(row.id) for row in existing_links_result}

            if set(product_ids) - set(existing_links.keys()):
                SupplierException.cant_find_link()

            updates = []
            item_dict = {item.product_id: item for item in supplier_data.update_products}

            for product_id in product_ids:
                item = item_dict[product_id]

                update_data = {
                    "id": existing_links[product_id],
                    "updated_at": datetime.now()
                }

                if item.is_active is not None:
                    update_data["is_active"] = item.is_active
                if item.notes is not None:
                    update_data["notes"] = item.notes

                updates.append(update_data)

            if updates:
                statement = update(Supplier_Product)
                await session.execute(statement, updates)

        await session.commit()
