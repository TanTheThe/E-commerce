from datetime import datetime
import select
from typing import List, Set
from sqlalchemy import func, update, delete
from sqlalchemy.orm import selectinload
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product.repositories import ProductRepository
from src.crud.supplier.repositories import SupplierRepository
from src.database.models import Supplier, Product, Supplier_Product
from src.errors.product import ProductException
from src.errors.supplier import SupplierException
from src.schemas.supplier import SupplierProductUpdate, SupplierUpdate

supplier_repository = SupplierRepository()
product_repository = ProductRepository()


class UpdateSupplierService:
    async def update_supplier(self, supplier_id: str, supplier_data: SupplierUpdate, session: AsyncSession):
        condition = [Supplier.id == supplier_id]
        supplier = await supplier_repository.get_supplier(session=session, where_conditions=condition)
        if not supplier:
            SupplierException.supplier_not_found()
            
        if supplier_data.name and supplier_data.name != supplier.name:
            condition = [
                func.lower(Supplier.name) == supplier_data.name.lower(),
                Supplier.id != supplier_id
            ]
            
            existing = await supplier_repository.get_supplier(
                session=session, 
                where_conditions=condition
            )
            
            if existing:
                SupplierException.name_supplier_already_exists()
                
        if self.has_basic_updates(supplier_data):
            await self.update_basic_info(supplier_id, supplier_data, session)
            
        all_product_ids = self.collect_all_product_ids(supplier_data)
        
        if not all_product_ids:
            return

        if supplier_data.add_products:
            add_product_ids = {p.product_id for p in supplier_data.add_products}
            await self.validate_products_exist(list(add_product_ids), session)
        
        existing_links_result, _ = await supplier_repository.get_all_suppliers_product(
            session=session,
            where_conditions=[Supplier_Product.supplier_id == supplier_id, Supplier_Product.product_id.in_(all_product_ids)]
        )

        existing_links = {str(row.product_id): str(row.id) for row in existing_links_result}
        
        if supplier_data.remove_product_ids:
            missing_links = set(supplier_data.remove_product_ids) - set(existing_links.keys())
            if missing_links:
                raise SupplierException.products_not_linked_to_supplier(
                    product_ids=list(missing_links)
                )
                
            delete_stmt = delete(Supplier_Product).where(
                and_(
                    Supplier_Product.supplier_id == supplier_id,
                    Supplier_Product.product_id.in_(supplier_data.remove_product_ids)
                )
            )

            await session.execute(delete_stmt)
            
        if supplier_data.add_products:
            await self.add_products(
                supplier_id, supplier_data.add_products, existing_links, session
            )

        if supplier_data.update_products:
            await self.update_products(
                supplier_id, supplier_data.update_products, existing_links, session
            )

        await session.commit()
        await session.refresh(supplier)
        
        return await self.get_updated_supplier_data(supplier_id, session)
        
        
    def has_basic_updates(self, supplier_data: SupplierUpdate) -> bool:
        basic_fields = {
            'name', 'contact_person', 'phone', 'email', 'address',
            'bank_account', 'bank_name', 'credit_limit', 'is_active', 'notes'
        }
        
        update_dict = supplier_data.model_dump(exclude_unset=True)
        return any(field in update_dict for field in basic_fields)


    async def update_basic_info(self, supplier_id: str, supplier_data: SupplierUpdate, session: AsyncSession):
        update_data = supplier_data.model_dump(
            exclude_unset=True,
            exclude={'add_products', 'remove_product_ids', 'update_products'}
        )
        
        if update_data:
            update_data['updated_at'] = datetime.now()
            condition = and_(Supplier.id == supplier_id)
            await supplier_repository.update_supplier(condition, update_data, session)
            
            
    def collect_all_product_ids(self, supplier_data: SupplierUpdate) -> Set[str]:
        all_ids = set()
        
        if supplier_data.add_products:
            all_ids.update(p.product_id for p in supplier_data.add_products)
        
        if supplier_data.remove_product_ids:
            all_ids.update(supplier_data.remove_product_ids)
        
        if supplier_data.update_products:
            all_ids.update(p.product_id for p in supplier_data.update_products)
        
        return all_ids
    
    
    async def validate_products_exist(self, product_ids: List[str], session: AsyncSession):
        if not product_ids:
            return
        
        conditions = [Product.id.in_(product_ids)]
        _, count = await product_repository.get_all_product(session=session, where_conditions=conditions)
        
        if count != len(product_ids):
            raise ProductException.some_products_not_exists()
        
        
    async def add_products(self, supplier_id: str, add_products: List[SupplierProductUpdate],
                           existing_links: dict, session: AsyncSession):
        now = datetime.now()
        updates = []
        new_items = []

        for item in add_products:
            if item.product_id in existing_links:
                update_data = {
                    "id": existing_links[item.product_id],
                    "is_active": item.is_active if item.is_active is not None else True,
                    "notes": item.notes,
                    "updated_at": now
                }
                updates.append(update_data)
            else:
                new_items.append({
                    'supplier_id': supplier_id,
                    'product_id': item.product_id,
                    'is_active': item.is_active if item.is_active is not None else True,
                    'notes': item.notes,
                    'created_at': now,
                    'updated_at': now
                })

        if updates:
            stmt = update(Supplier_Product)
            await session.execute(stmt, updates)
        
        if new_items:
            session.add_all([
                Supplier_Product(**item_data) for item_data in new_items
            ])
            
            
    async def update_products(self, supplier_id: str, update_products: List[SupplierProductUpdate], 
                              existing_links: dict, session: AsyncSession):
        update_product_ids = {p.product_id for p in update_products}
        missing_links = update_product_ids - set(existing_links.keys())
        
        if missing_links:
            raise SupplierException.products_not_linked_to_supplier(
                product_ids=list(missing_links)
            )
            
        now = datetime.now()
        updates = []
        
        for item in update_products:
            update_data = {
                "id": existing_links[item.product_id],
                "updated_at": now
            }
            
            if item.is_active is not None:
                update_data["is_active"] = item.is_active
            
            if item.notes is not None:
                update_data["notes"] = item.notes
            
            updates.append(update_data)
            
        if updates:
            stmt = update(Supplier_Product)
            await session.execute(stmt, updates)
            
    
    async def get_updated_supplier_data(self, supplier_id: str, session: AsyncSession):
        conditions = [Supplier.id == supplier_id]
        options = [selectinload(Supplier.supplier_products)]
        
        supplier = await supplier_repository.get_supplier(
            session=session,
            where_conditions=conditions,
            options=options
        )
        
        active_products = sum(
            1 for sp in supplier.supplier_products if sp.is_active
        )
        
        return {
            "id": str(supplier.id),
            "code": supplier.code,
            "name": supplier.name,
            "contact_person": supplier.contact_person,
            "phone": supplier.phone,
            "email": supplier.email,
            "credit_limit": supplier.credit_limit,
            "current_debt": supplier.current_debt,
            "is_active": supplier.is_active,
            "total_products": len(supplier.supplier_products),
            "active_products": active_products,
            "updated_at": supplier.updated_at.isoformat() if supplier.updated_at else None
        }
        
        
