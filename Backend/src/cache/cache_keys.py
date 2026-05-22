import hashlib

class CacheKeys:
    
    # AUTHENTICATION
    @staticmethod
    def jwt_blacklist(jti: str) -> str:
        """JWT Token Blacklist"""
        return f"auth:blacklist:jti:{jti}"
    
    @staticmethod
    def rate_limit_login(identifier: str) -> str:
        """Rate limit cho login (IP hoặc username)"""
        return f"rate_limit:login:{identifier}"
    
    @staticmethod
    def rate_limit_otp(user_id: str) -> str:
        """Rate limit cho OTP request"""
        return f"rate_limit:otp:user:{user_id}"

    @staticmethod
    def get_account_lock_key(email: str):
        return f"auth:account_locked:{email}"

    @staticmethod
    def get_failed_attempts_key(email: str):
        return f"auth:failed_attempts:{email}"

    @staticmethod
    def check_ip_rate_limit_minute_key(ip_address: str):
        return f"rate_limit:login:ip:{ip_address}:minute"

    @staticmethod
    def check_ip_rate_limit_hour_key(ip_address: str):
        return f"rate_limit:login:ip:{ip_address}:hour"

    @staticmethod
    def forgot_password_rate_limit(email: str):
        return f"auth:forgot_password:rate:{email}"

    @staticmethod
    def otp(user_id: str):
        return f"auth:otp:{user_id}"

    @staticmethod
    def check_signup_rate_limit(ip_address: str):
        return f"auth:signup:rate:{ip_address}"

    @staticmethod
    def signup_cooldown(email: str):
        return f"auth:signup:cooldown:{email}"

    @staticmethod
    def verify_token(token: str):
        return f"auth:verification:token:{token}"

    @staticmethod
    def check_verify_rate_limit(user_id: str):
        return f"auth:verification:rate:{user_id}"

    @staticmethod
    def setup_2fa_rate_limit(user_id: str):
        return f"auth:2fa_setup:{user_id}"

    @staticmethod
    def setup_2fa(user_id: str):
        return f"auth:2fa_setup:{user_id}"

    @staticmethod
    def otp_verify_attempts(user_id: str):
        return f"auth:otp_verify_attempts:{user_id}"

    # PRODUCTS
    @staticmethod
    def product_filter_info_pattern() -> str:
        """Pattern để invalidate filter info cache"""
        return f"product:filter_info:*"

    @staticmethod
    def product_selectbox_pattern() -> str:
        """Pattern để invalidate products selectbox cache"""
        return f"product:selectbox:*"

    @staticmethod
    def product_variants_selectbox_pattern(product_id: str = None) -> str:
        """Pattern để invalidate variants selectbox cache"""
        if product_id:
            return f"product:variants_selectbox:product:{product_id}"
        return f"product:variants_selectbox:*"

    @staticmethod
    def product_list_all_pattern() -> str:
        """Pattern để invalidate tất cả product list cache"""
        return f"product:list:*"

    @staticmethod
    def product_popular_pattern() -> str:
        """Pattern để invalidate tất cả popular products cache"""
        return f"product:popular:*"

    @staticmethod
    def product_latest_pattern() -> str:
        """Pattern để invalidate latest products cache"""
        return f"product:latest:*"

    @staticmethod
    def product_top_discount_pattern() -> str:
        """Pattern để invalidate top discount cache"""
        return f"product:top_discount:*"

    @staticmethod
    def product_detail_customer_pattern() -> str:
        """Pattern để invalidate product detail cache"""
        return f"product:detail:customer:*"

    @staticmethod
    def product_related_pattern(product_id: str = None) -> str:
        """Pattern để invalidate related products cache"""
        if product_id:
            return f"product:related:{product_id}:*"
        return f"product:related:*"

    @staticmethod
    def product_list_params(category_identifier: str, filter_hash: str, skip: int, limit: int) -> str:
        return f"product:list:category:{category_identifier}:filter:{filter_hash}:skip:{skip}:limit:{limit}"

    @staticmethod
    def product_popular(parent_category_id: str, limit_per_category: int) -> str:
        return f"product:popular:parent:{parent_category_id}:limit:{limit_per_category}"

    @staticmethod
    def product_latest(limit_per_category: int) -> str:
        return f"product:latest:limit:{limit_per_category}"

    @staticmethod
    def product_related(product_id: str, price_range: float, limit_per_category: int) -> str:
        return f"product:related:{product_id}:range:{price_range}:limit:{limit_per_category}"

    @staticmethod
    def product_top_discount(limit: int) -> str:
        return f"product:top_discount:limit:{limit}"

    @staticmethod
    def product_filter_info(category_id: str) -> str:
        return f"product:filter_info:category:{category_id}"

    @staticmethod
    def product_detail_customer(identifier: str) -> str:
        return f"product:detail:customer:{identifier}"

    @staticmethod
    def product_selectbox(category_id: str, supplier_id: str) -> str:
        cat_part = f"cat:{category_id}" if category_id else "cat:all"
        sup_part = f"sup:{supplier_id}" if supplier_id else "sup:all"
        return f"product:selectbox:{cat_part}:{sup_part}"

    @staticmethod
    def variants_selectbox(product_id: str) -> str:
        return f"product:variants_selectbox:product:{product_id}"
    
    # CATEGORIES
    @staticmethod
    def category_tree() -> str:
        """Categories tree (hierarchical)"""
        return "category:tree:all"
    
    @staticmethod
    def category_detail(category_id: str) -> str:
        """Category detail"""
        return f"category:detail:{category_id}"

    @staticmethod
    def category_list_customer(skip: int = 0, limit: int = 10) -> str:
        """Customer-facing category list (paginated, no filters)"""
        return f"category:list:customer:skip:{skip}:limit:{limit}"

    @staticmethod
    def category_list_customer_pattern() -> str:
        """Pattern to invalidate all customer category lists"""
        return "category:list:customer:*"

    @staticmethod
    def category_resolve(identifier: str) -> str:
        """Category ID resolved from slug or other identifier"""
        return f"category:resolve:{identifier}"

    @staticmethod
    def category_resolve_pattern() -> str:
        """Pattern to invalidate all category resolve mappings"""
        return "category:resolve:*"
    
    # ORDERS
    @staticmethod
    def order_detail(order_id: str) -> str:
        """Order detail"""
        return f"order:detail:{order_id}"

    @staticmethod
    def order_detail_admin(order_id: str) -> str:
        return f"{CacheKeys.order_detail(order_id)}:admin"

    @staticmethod
    def order_detail_customer(order_id: str, customer_id: str) -> str:
        return f"{CacheKeys.order_detail(order_id)}:customer:{customer_id}"
    
    @staticmethod
    def order_list_user(user_id: str, page: int = 1) -> str:
        """Order history của user"""
        return f"order:list:user:{user_id}:page:{page}"

    @staticmethod
    def order_list_user_with_status(cache_key: str, status_order: str) -> str:
        return f"{cache_key}:status:{status_order}"

    @staticmethod
    def cancellation_pending_page_1() -> str:
        return "order:cancellation:pending:page:1"

    @staticmethod
    def create_order_rate_limit(ip_address: str) -> str:
        return f"rate_limit:order:create:user:{ip_address}"

    @staticmethod
    def analytics() -> str:
        """Pattern xóa toàn bộ analytics cache"""
        return "analytics:*"

    @staticmethod
    def order_list_user_without_page(user_id: str) -> str:
        """Pattern xóa toàn bộ cache danh sách order của user"""
        return f"order:list:user:{user_id}:*"

    @staticmethod
    def cart_user(user_id: str) -> str:
        """Pattern xóa toàn bộ cache cart của user"""
        return f"cart:*:user:{user_id}*"
    
    # SPECIAL OFFERS
    @staticmethod
    def special_offer_admin_list_pattern() -> str:
        """Pattern để invalidate admin offers list cache"""
        return f"special_offer:admin:*"

    @staticmethod
    def special_offer_customer_list_pattern(user_id: str = None) -> str:
        """Pattern để invalidate customer offers cache"""
        if user_id:
            return f"special_offer:customer:user:{user_id}:*"
        return f"special_offer:customer:*"

    @staticmethod
    def special_offer_admin_filters(filter_hash: str, skip: int, limit: int) -> str:
        return f"special_offer:admin:filter:{filter_hash}:skip:{skip}:limit:{limit}"

    @staticmethod
    def special_offer_customer_filters(user_id: str, search_hash: str, skip: int, limit: int) -> str:
        return f"special_offer:customer:user:{user_id}:search:{search_hash}:skip:{skip}:limit:{limit}"
    
    # USER
    @staticmethod
    def user_profile_pattern(user_id: str = None) -> str:
        """Pattern để invalidate user profile cache"""
        if user_id:
            return f"user:profile:*:{user_id}"
        return f"user:profile:*"

    # COLOR
    @staticmethod
    def color_list(skip: int = 0, limit: int = 10) -> str:
        """Color list (paginated, no search filter)"""
        return f"color:list:skip:{skip}:limit:{limit}"

    @staticmethod
    def color_list_pattern() -> str:
        """Pattern to invalidate all color lists"""
        return "color:list:*"

    # ANALYTICS
    @staticmethod
    def analytics_overview_key(period: str = None, calculated_from=None, calculated_to=None) -> str:
        """Cache key cho analytics overview"""
        if calculated_from and calculated_to:
            date_hash = hashlib.md5(
                f"{calculated_from.isoformat()}:{calculated_to.isoformat()}".encode()
            ).hexdigest()[:8]

            return f"analytics:overview:custom:{date_hash}"

        return f"analytics:overview:{period}"

    # STOCK
    @staticmethod
    def stock_warehouse_summary(warehouse_id: str) -> str:
        return f"stock:warehouse:{warehouse_id}:summary"

    @staticmethod
    def low_stock_items(warehouse_id: str, severity_str: str, skip: int, limit: int) -> str:
        warehouse_part = f"warehouse:{warehouse_id}" if warehouse_id else "all_warehouses"
        severity_part = f"severity:{severity_str}" if severity_str else "all_severity"

        return f"stock:low_stock:{warehouse_part}:{severity_part}:skip:{skip}:limit:{limit}"

    @staticmethod
    def low_stock_items_without_filter(warehouse_id: str) -> str:
        return f"stock:low_stock:warehouse:{warehouse_id}:*"

    @staticmethod
    def stock_warehouse_filters(warehouse_id: str) -> str:
        return f"stock:warehouse:{warehouse_id}:filters"

    @staticmethod
    def stock_warehouse_products(warehouse_id: str) -> str:
        return f"stock:warehouse:{warehouse_id}:product:*"