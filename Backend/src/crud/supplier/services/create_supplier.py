from datetime import datetime
from typing import List
from sqlalchemy import func
from src.crud.product.repositories import ProductRepository
from src.crud.supplier.repositories import SupplierRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Supplier, Product, Supplier_Product
from src.errors.product import ProductException
from src.errors.supplier import SupplierException
from src.schemas.supplier import SupplierCreate, SupplierProductCreate

supplier_repository = SupplierRepository()
product_repository = ProductRepository()


class CreateSupplierService:
    async def create_supplier(self, supplier_data: SupplierCreate, session: AsyncSession):
        await self.validate_unique_name(supplier_data.name, session)

        if supplier_data.products:
            await self.validate_products_exist(supplier_data.products, session)

        supplier_dict = supplier_data.model_dump(exclude={'products'})
        supplier_dict["code"] = await supplier_repository.generate_supplier_code(session)

        supplier = await supplier_repository.create_supplier(supplier_dict, session)

        if supplier_data.products:
            await self.link_products_to_supplier(str(supplier.id), supplier_data.products, session)

        await session.commit()
        await session.refresh(supplier)

        product_count = len(supplier_data.products) if supplier_data.products else 0

        return {
            "id": str(supplier.id),
            "code": supplier.code,
            "name": supplier.name,
            "contact_person": supplier.contact_person,
            "phone": supplier.phone,
            "email": supplier.email,
            "address": supplier.address,
            "bank_account": supplier.bank_account,
            "bank_name": supplier.bank_name,
            "credit_limit": supplier.credit_limit,
            "current_debt": supplier.current_debt,
            "is_active": supplier.is_active,
            "notes": supplier.notes,
            "product_count": product_count,
            "created_at": supplier.created_at.isoformat() if hasattr(supplier, 'created_at') else None
        }


    async def validate_unique_name(self, name: str, session: AsyncSession):
        conditions = [func.lower(Supplier.name) == func.lower(name)]
        existing = await supplier_repository.get_supplier(session=session, where_conditions=conditions)

        if existing:
            SupplierException.name_supplier_already_exists()


    async def validate_products_exist(self, products: List[SupplierProductCreate], session: AsyncSession):
        product_ids = [p.product_id for p in products]

        condition = [Product.id.in_(product_ids)]
        existing_products, _ = await product_repository.get_all_product(
            session=session,
            where_conditions=condition
        )

        if len(existing_products) != len(product_ids):
            ProductException.some_products_not_exists()


    async def link_products_to_supplier(self, supplier_id: str, products: List[SupplierProductCreate], session: AsyncSession):
        new_objects = [
            Supplier_Product(
                supplier_id=supplier_id,
                product_id=product_input.product_id,
                is_active=product_input.is_active if hasattr(product_input, 'is_active') else True,
                notes=product_input.notes,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for product_input in products
        ]
        session.add_all(new_objects)









