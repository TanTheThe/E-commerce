from fastapi import APIRouter

from src.crud.cart.routes import cart_admin_router, cart_customer_router, cart_common_router
from src.crud.color.routes import color_admin_router, color_customer_router, color_common_router
from src.crud.material.routes import material_admin_router, material_customer_router, material_common_router
from src.crud.notification.routes import notification_admin_router, notification_customer_router, \
    notification_common_router
from src.crud.return_order.routes import return_order_admin_router, return_order_customer_router, \
    return_order_common_router
from src.crud.size.routes import size_admin_router, size_customer_router, size_common_router
from src.crud.tag.routes import tag_admin_router, tag_customer_router, tag_common_router
from src.crud.user.routes import user_admin_router, user_common_router, user_customer_router
from src.crud.authentication.routes import auth_admin_router, auth_customer_router, auth_common_router
from src.crud.address.routes import address_admin_router, address_customer_router, address_common_router
from src.crud.categories.routes import categories_admin_router, categories_customer_router, categories_common_router
from src.crud.product.routes import product_admin_router, product_customer_router, product_common_router
from src.crud.special_offer.routes import special_offer_admin_router, special_offer_customer_router, special_offer_common_router
from src.crud.order.routes import order_admin_router, order_customer_router, order_common_router
from src.crud.evaluate.routes import evaluate_admin_router, evaluate_customer_router, evaluate_common_router
from src.crud.vnpay.routes import vnpay_admin_router, vnpay_customer_router, vnpay_common_router
from src.crud.brand.routes import brand_admin_router, brand_customer_router, brand_common_router

version = "v1"
api_router = APIRouter(prefix=f"/api/{version}")

admin_router = APIRouter(prefix="/admin", tags=["user-admin"])
admin_router.include_router(user_admin_router)
admin_router.include_router(auth_admin_router)
admin_router.include_router(address_admin_router)
admin_router.include_router(categories_admin_router)
admin_router.include_router(product_admin_router)
admin_router.include_router(special_offer_admin_router)
admin_router.include_router(order_admin_router)
admin_router.include_router(evaluate_admin_router)
admin_router.include_router(color_admin_router)
admin_router.include_router(size_admin_router)
admin_router.include_router(cart_admin_router)
admin_router.include_router(vnpay_admin_router)
admin_router.include_router(notification_admin_router)
admin_router.include_router(return_order_admin_router)
admin_router.include_router(brand_admin_router)
admin_router.include_router(material_admin_router)
admin_router.include_router(tag_admin_router)

customer_router = APIRouter(prefix="/customer", tags=["user-customer"])
customer_router.include_router(user_customer_router)
customer_router.include_router(auth_customer_router)
customer_router.include_router(address_customer_router)
customer_router.include_router(categories_customer_router)
customer_router.include_router(product_customer_router)
customer_router.include_router(special_offer_customer_router)
customer_router.include_router(order_customer_router)
customer_router.include_router(evaluate_customer_router)
customer_router.include_router(color_customer_router)
customer_router.include_router(size_customer_router)
customer_router.include_router(cart_customer_router)
customer_router.include_router(vnpay_customer_router)
customer_router.include_router(notification_customer_router)
customer_router.include_router(return_order_customer_router)
customer_router.include_router(brand_customer_router)
customer_router.include_router(material_customer_router)
customer_router.include_router(tag_customer_router)

public_router = APIRouter(prefix="/general", tags=["user-common"])
public_router.include_router(user_common_router)
public_router.include_router(auth_common_router)
public_router.include_router(address_common_router)
public_router.include_router(categories_common_router)
public_router.include_router(product_common_router)
public_router.include_router(special_offer_common_router)
public_router.include_router(order_common_router)
public_router.include_router(evaluate_common_router)
public_router.include_router(color_common_router)
public_router.include_router(size_common_router)
public_router.include_router(cart_common_router)
public_router.include_router(vnpay_common_router)
public_router.include_router(notification_common_router)
public_router.include_router(return_order_common_router)
public_router.include_router(brand_common_router)
public_router.include_router(material_common_router)
public_router.include_router(tag_common_router)