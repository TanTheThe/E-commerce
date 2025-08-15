from sqlalchemy.orm import selectinload, joinedload, noload, load_only
from src.database.models import Special_Offer, User, Address, Order, Order_Detail, Product_Variant, Product
from src.crud.address.repositories import AddressRepository
from src.crud.order.repositories import OrderRepository
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.user.repositories import UserRepository
from src.crud.product.repositories import ProductRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, func, or_, asc, desc
from src.errors.address import AddressException
from src.errors.order import OrderException
from src.errors.product import ProductException
from src.schemas.order import OrderCreateModel, OrderFilterModel
import time
import asyncio
from src.errors.authentication import AuthException

order_repository = OrderRepository()
special_offer_repository = SpecialOfferRepository()
user_repository = UserRepository()
address_repository = AddressRepository()
product_repository = ProductRepository()
order_detail_repository = OrderDetailRepository()
product_variant_repository = ProductVariantRepository()


class OrderService:
    async def validate_order_dependencies(self, customer_id, address_id, offer_id, session):
        # Mỗi phần tử là 1 lời gọi đến DB
        joins_user = [
            noload(User.address),
            noload(User.order),
            noload(User.evaluate),
        ]
        conditions_user = and_(User.id == customer_id, User.deleted_at.is_(None))

        joins_address = [
            noload(Address.user),
        ]
        conditions_address = and_(Address.id == address_id, Address.deleted_at.is_(None))

        tasks = [
            user_repository.get_user(conditions_user, session, joins_user),
            address_repository.get_address(conditions_address, session, joins_address),
        ]

        # Nếu có offer_id, thì thêm một tác vụ nữa để truy vấn ưu đãi đó.
        if offer_id:
            joins_special_offer = [
                noload(Special_Offer.products),
            ]
            conditions_address = and_(Special_Offer.id == offer_id, Special_Offer.deleted_at.is_(None))
            tasks.append(special_offer_repository.get_special_offer(conditions_address, session, joins_special_offer))

        # Nếu không có ưu đãi, ta vẫn append() một cái gì đó để giữ thứ tự kết quả, vì gather() trả về theo đúng thứ tự các coroutine trong danh sách.
        else:
            tasks.append(asyncio.sleep(0))  # placeholder giữ thứ tự

        # Chạy tất cả coroutine trong tasks cùng lúc, và trả về kết quả sau khi tất cả xong.
        customer, address, special_offer = await asyncio.gather(*tasks)

        if not customer:
            AuthException.user_not_found()

        if not address:
            AddressException.not_found()

        return customer, address, special_offer


    async def create_order(self, customer_id: str, order_data: OrderCreateModel, session: AsyncSession):
        variant_ids = {item.product_variant_id for item in order_data.order_detail}
        condition = Product_Variant.id.in_(variant_ids)
        joins = [
            selectinload(Product_Variant.product).options(
                noload(Product.order_detail),
                noload(Product.product_variant),
                noload(Product.evaluate),
                noload(Product.categories),
                noload(Product.special_offer),
                noload(Product.categories_product),
            ).load_only(
                Product.id,
                Product.name,
                Product.images,
            )
        ]
        variants = await product_variant_repository.get_all_product_variant(condition, session, joins)
        variant_map = {}
        order_detail_objs = []
        sub_total = 0
        for item in order_data.order_detail:
            variant = next((v for v in variants if str(v.id) == item.product_variant_id), None)
            if not variant:
                ProductException.not_found_variant()

            product = variant.product
            if not product:
                ProductException.not_found()

            if item.quantity > variant.quantity:
                ProductException.out_of_stock(str(variant.id))

            sub_total += item.quantity * variant.price
            product_dict = {
                "name": product.name,
                "images": product.images,
                "price": variant.price,
                "quantity": variant.quantity,
                "size": variant.size,
                "color": variant.color
            }

            order_detail_dict = {
                "quantity": item.quantity,
                "price": variant.price,
                "product_id": variant.product_id,
                "product_variant_id": variant.id,
                "Product": product_dict
            }

            order_detail_objs.append(Order_Detail(**order_detail_dict))
            variant_map[str(variant.id)] = (variant, item.quantity)

        customer, address, special_offer = await self.validate_order_dependencies(
            customer_id, order_data.address_id, order_data.special_offer_id, session
        )

        discount = 0
        if special_offer and (special_offer.condition is None or sub_total >= special_offer.condition):
            if special_offer.type == "percent":
                discount = int(sub_total * special_offer.discount / 100)
            elif special_offer.type == "fixed":
                discount = special_offer.discount

        total_price = sub_total - discount

        address_dict = {
            "line": address.line,
            "street": address.street,
            "ward": address.ward,
            "city": address.city,
            "district": address.district,
            "country": address.country
        }

        new_order_dict = {
            "code": str(int(time.time() * 1000)),
            "sub_total": sub_total,
            "total_price": total_price,
            "discount": discount,
            "note": order_data.note,
            "payment_method": "vnpay",
            "transaction_no": "",
            "user_id": customer_id,
            "Address": address_dict
        }

        new_order = await order_repository.create_order(new_order_dict, session)
        for od in order_detail_objs:
            od.order_id = new_order.id

        await order_detail_repository.create_order_detail(order_detail_objs, session)

        for variant, ordered_quantity in variant_map.values():
            variant.quantity -= ordered_quantity
            session.add(variant)

        await session.commit()

        response = {
            "order_id": str(new_order.id),
            "sub_total": sub_total,
            "total_price": total_price,
            "note": new_order.note,
            "special_offer": {
                "id": str(special_offer.id),
                "code": special_offer.code,
                "name": special_offer.name,
                "discount": special_offer.discount,
                "condition": special_offer.condition,
                "type": special_offer.type,
            } if special_offer else None,
            "address": {
                "id": str(address.id),
                "line": address.line,
                "street": address.street,
                "ward": address.ward,
                "city": address.city,
                "district": address.district,
                "country": address.country,
            },
            "order_detail": [
                {
                    "quantity": od.quantity,
                    "price": str(od.price),
                    "product_id": str(od.product_id),
                    "product_variant_id": str(od.product_variant_id)
                }
                for od in order_detail_objs
            ]
        }

        return response


    async def get_detail_order_admin(self, order_id: str, session: AsyncSession):
        joins = [
            selectinload(Order.order_detail).options(
                noload(Order_Detail.product),
                noload(Order_Detail.product_variant),
                noload(Order_Detail.order),
                noload(Order_Detail.evaluate),
            ).load_only(
                Order_Detail.id,
                Order_Detail.Product
            ),
            selectinload(Order.user).options(
                noload(User.address),
                noload(User.order),
                noload(User.evaluate),
            ).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.email,
                User.phone,
            ),
        ]

        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        order = await order_repository.get_order(condition, session, joins)

        if not order:
            OrderException.not_found()

        user = order.user
        user_response = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
        } if user else None

        address = order.Address
        address_response = {
            "line": address.get("line"),
            "street": address.get("street"),
            "ward": address.get("ward"),
            "city": address.get("city"),
            "district": address.get("district"),
            "country": address.get("country"),
        } if address else None

        order_detail_response = []
        for od in order.order_detail:
            product_snapshot = od.Product

            product_dict = {
                "id": str(od.id),
                "name": product_snapshot.get("name"),
                "images": product_snapshot.get("images", []),
                "price": product_snapshot.get("price"),
                "quantity": product_snapshot.get("quantity"),
                "size": product_snapshot.get("size"),
                "color": product_snapshot.get("color"),
            }

            order_detail_response.append(product_dict)

        response = {
            "order": {
                "id": str(order.id),
                "code": order.code,
                "note": order.note,
                "status": order.status,
                "created_at": str(order.created_at),
                "sub_total": order.sub_total,
                "discount": order.discount,
                "total_price": order.total_price,
            },
            "customer": user_response,
            "address": address_response,
            "order_detail": order_detail_response
        }

        return response


    async def get_detail_order_customer(self, order_id: str, customer_id: str, session: AsyncSession):
        joins = [
            selectinload(Order.order_detail).selectinload(Order_Detail.product),
            selectinload(Order.order_detail).selectinload(Order_Detail.product_variant),
            selectinload(Order.user),
        ]

        condition = and_(Order.id == order_id)
        order = await order_repository.get_order(condition, session, joins)

        if not order:
            OrderException.not_found()

        if str(order.user_id) != str(customer_id):
            OrderException.unauthorized_order()

        user = order.user
        user_response = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
        } if user else None

        address = order.Address
        address_response = {
            "line": address["line"],
            "street": address["street"],
            "ward": address["ward"],
            "city": address["city"],
            "district": address["district"],
            "country": address["country"],
        } if address else None

        order_detail_response = []
        for od in order.order_detail:
            product = od.product
            variant = od.product_variant

            if product and variant:
                product_dict = {
                    "name": product.name,
                    "images": product.images,
                    "price": variant.price if variant else None,
                    "quantity": variant.quantity if variant else None,
                    "size": variant.size if variant else None,
                    "color": variant.color if variant else None,
                }
            else:
                product_dict = {}

            order_detail_response.append(product_dict)

        response = {
            "order": {
                "code": order.code,
                "note": order.note,
                "status": order.status,
                "created_at": str(order.created_at),
                "sub_total": order.sub_total,
                "discount": order.discount,
                "total_price": order.total_price,
            },
            "customer": user_response,
            "address": address_response,
            "order_detail": order_detail_response
        }

        return response


    async def get_all_order_admin(self, session: AsyncSession, filter_data: OrderFilterModel, skip: int = 0, limit: int = 10):
        conditions = [Order.deleted_at.is_(None), User.deleted_at.is_(None)]

        if filter_data.search:
            search_term = f"%{filter_data.search}%"
            full_name_search = func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
            conditions.append(or_(
                Order.code.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                full_name_search
            ))
            need_user_join = True
        else:
            need_user_join = False

        if filter_data.status:
            conditions.append(Order.status == filter_data.status)

        order_by = []
        if filter_data.sort_by_total_price:
            if filter_data.sort_by_total_price == "cheapest":
                order_by.append(asc(Order.total_price))
            else:
                order_by.append(desc(Order.total_price))

        if filter_data.sort_by_created_at:
            if filter_data.sort_by_created_at == "newest":
                order_by.append(desc(Order.created_at))
            else:
                order_by.append(asc(Order.created_at))

        joins = [joinedload(Order.user).options(
                     noload(User.address),
                     noload(User.order),
                     noload(User.evaluate),
                 ).load_only(
                     User.id,
                     User.first_name,
                     User.last_name,
                     User.deleted_at,
                 )]
        orders, total = await order_repository.get_all_order(conditions, session, order_by, skip=skip, limit=limit, joins=joins, join_user=need_user_join)

        response = []
        for order in orders:
            user = order.user
            customer_name = f"{user.first_name} {user.last_name}" if user else None

            order_dict = {
                "id": str(order.id),
                "code": order.code,
                "status": order.status,
                "created_at": str(order.created_at),
                "total_price": order.total_price,
                "sub_total": order.sub_total,
                "discount": order.discount,
                "customer_name": customer_name,
                "payment_method": order.payment_method,
            }
            response.append(order_dict)

        return {
            "data": response,
            "total": total,
        }


    async def get_all_order_customer(self, user_id: str, session: AsyncSession, skip: int = 0, limit: int = 10):
        condition = and_(Order.user_id == user_id)
        orders = await order_repository.get_all_order(condition, session, skip=skip, limit=limit)

        response = []
        for order in orders:
            order_dict = {
                "code": order.code,
                "status": order.status,
                "created_at": str(order.created_at),
                "total_price": order.total_price,
            }
            response.append(order_dict)

        return response


    async def update_status(self, order_id, status, session: AsyncSession):
        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        joins = [
            load_only(Order.status),
            noload(Order.user),
            noload(Order.order_detail),
        ]
        order_to_update = await order_repository.get_order(condition, session, joins)

        if order_to_update is None:
            OrderException.not_found()

        status_dict = status.model_dump()

        order_after_update = await order_repository.update_order(order_to_update, status_dict, session)

        return order_after_update


    async def count_new_orders(self, to_date, from_date, session: AsyncSession):
        condition = and_(Order.created_at >= from_date, Order.created_at <= to_date)
        orders = await order_repository.count_orders(condition, session)

        if orders is None:
            OrderException.not_found()

        return len(orders)


    async def get_total_sales(self, today, seven_days_ago, session: AsyncSession):
        condition = and_(Order.created_at >= seven_days_ago, Order.status == "Delivered")
        column_expr = func.coalesce(func.sum(Order.sub_total), 0)
        total_sales = await order_repository.get_statistics(column_expr, condition, session)

        if total_sales is None:
            OrderException.fail_get_total_sales()

        return total_sales

    async def get_total_revenue(self, today, seven_days_ago, session: AsyncSession):
        condition = and_(Order.created_at >= seven_days_ago, Order.status == "Delivered")
        column_expr = func.coalesce(func.sum(Order.total_price), 0)
        total_revenue = await order_repository.get_statistics(column_expr, condition, session)

        if total_revenue is None:
            OrderException.fail_get_total_revenue()

        return total_revenue











