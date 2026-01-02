
class CacheKeys:
    """Cache key patterns cho toàn bộ ứng dụng"""
    
    # ================================== AUTHENTICATION ==================================

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
    def failed_login_attempts(identifier: str) -> str:
        """Track failed login attempts"""
        return f"auth:failed_attempts:{identifier}"
    
    @staticmethod
    def user_session(session_id: str) -> str:
        """User session data"""
        return f"session:user:{session_id}"
    
    @staticmethod
    def setup_2fa_attempt(user_id: str) -> str:
        """2FA setup attempts"""
        return f"auth:2fa_setup:{user_id}"
    
    # ================================== PRODUCTS ================================== 
    @staticmethod
    def product_detail(product_id: str) -> str:
        """Product detail với variants, colors, sizes"""
        return f"product:detail:{product_id}"
    
    @staticmethod
    def product_list_category(category_id: str, page: int = 1) -> str:
        """Product list theo category với phân trang"""
        return f"product:list:category:{category_id}:page:{page}"
    
    @staticmethod
    def product_variants(product_id: str) -> str:
        """Product variants"""
        return f"product:variants:{product_id}"
    
    @staticmethod
    def product_search(keyword: str, page: int = 1) -> str:
        """Search results"""
        return f"search:results:keyword:{keyword}:page:{page}"
    
    @staticmethod
    def popular_products(limit: int = 10) -> str:
        """Popular products (sorted set)"""
        return f"analytics:popular_products:top:{limit}"
    
    # ================================== CATEGORIES ==================================
    @staticmethod
    def category_tree() -> str:
        """Categories tree (hierarchical)"""
        return "category:tree:all"
    
    @staticmethod
    def category_detail(category_id: str) -> str:
        """Category detail"""
        return f"category:detail:{category_id}"
    
    @staticmethod
    def category_products_count(category_id: str) -> str:
        """Count products trong category"""
        return f"category:products_count:{category_id}"
    
    # ================================== BRANDS ==================================
    @staticmethod
    def brand_list() -> str:
        """All brands"""
        return "brand:list:all"
    
    @staticmethod
    def brand_detail(brand_id: str) -> str:
        """Brand detail"""
        return f"brand:detail:{brand_id}"
    
    # ================================== CART ==================================
    @staticmethod
    def cart_user(user_id: str) -> str:
        """Cart của user đã login"""
        return f"cart:user:{user_id}"
    
    @staticmethod
    def cart_guest(session_id: str) -> str:
        """Cart của guest"""
        return f"cart:guest:session:{session_id}"
    
    @staticmethod
    def cart_items_count(user_id: str) -> str:
        """Cart items count (badge)"""
        return f"cart:count:user:{user_id}"
    
    @staticmethod
    def cart_total(user_id: str) -> str:
        """Cart total price"""
        return f"cart:total:user:{user_id}"
    
    # ==================== STOCK & INVENTORY ====================
    @staticmethod
    def stock_product(product_id: str, warehouse_id: str = None) -> str:
        """Stock của product (tất cả warehouse hoặc specific)"""
        if warehouse_id:
            return f"stock:warehouse:{warehouse_id}:product:{product_id}"
        return f"stock:product:{product_id}:all_warehouses"
    
    @staticmethod
    def stock_available(product_variant_id: str) -> str:
        """Available stock cho variant"""
        return f"stock:available:variant:{product_variant_id}"
    
    @staticmethod
    def stock_reservation(reservation_id: str) -> str:
        """Stock reservation during checkout"""
        return f"stock:reservation:{reservation_id}"
    
    @staticmethod
    def low_stock_alert() -> str:
        """Low stock products (sorted set)"""
        return "stock:alerts:low_stock"
    
    # ================================== ORDERS ==================================
    @staticmethod
    def order_detail(order_id: str) -> str:
        """Order detail"""
        return f"order:detail:{order_id}"
    
    @staticmethod
    def order_list_user(user_id: str, page: int = 1) -> str:
        """Order history của user"""
        return f"order:list:user:{user_id}:page:{page}"
    
    @staticmethod
    def order_status(order_id: str) -> str:
        """Order status tracking"""
        return f"order:status:{order_id}"
    
    # ================================== SPECIAL OFFERS ==================================
    @staticmethod
    def offers_active() -> str:
        """All active special offers"""
        return "offer:active:all"
    
    @staticmethod
    def offers_user(user_id: str) -> str:
        """User-specific offers"""
        return f"offer:user:{user_id}"
    
    @staticmethod
    def offer_detail(offer_id: str) -> str:
        """Offer detail"""
        return f"offer:detail:{offer_id}"
    
    @staticmethod
    def offer_eligible(user_id: str, offer_id: str) -> str:
        """Check if user eligible for offer"""
        return f"offer:eligible:user:{user_id}:offer:{offer_id}"
    
    # ================================== LOCATION ==================================
    @staticmethod
    def provinces() -> str:
        """All provinces"""
        return "location:provinces:all"
    
    @staticmethod
    def wards_by_province(province_id: str) -> str:
        """Wards by province"""
        return f"location:wards:province:{province_id}"
    
    @staticmethod
    def address_user(user_id: str) -> str:
        """User addresses"""
        return f"user:addresses:{user_id}"
    
    # ================================== USER ==================================
    @staticmethod
    def user_profile(user_id: str) -> str:
        """User profile data"""
        return f"user:profile:{user_id}"
    
    @staticmethod
    def user_permissions(user_id: str) -> str:
        """User permissions/role"""
        return f"user:permissions:{user_id}"
    
    # ================================== ANALYTICS ==================================
    @staticmethod
    def analytics_dashboard() -> str:
        """Dashboard metrics"""
        return "analytics:dashboard:metrics"
    
    @staticmethod
    def analytics_revenue(period: str = "today") -> str:
        """Revenue stats (today, week, month)"""
        return f"analytics:revenue:{period}"
    
    @staticmethod
    def analytics_top_customers(limit: int = 10) -> str:
        """Top customers (sorted set)"""
        return f"analytics:top_customers:limit:{limit}"
    
    # ================================== SUPPLIERS ==================================
    @staticmethod
    def supplier_list() -> str:
        """All suppliers"""
        return "supplier:list:all"
    
    @staticmethod
    def supplier_products(supplier_id: str) -> str:
        """Products by supplier"""
        return f"supplier:products:{supplier_id}"
    
    # ================================== MATERIALS & TAGS ==================================
    @staticmethod
    def materials_list() -> str:
        """All materials"""
        return "material:list:all"
    
    @staticmethod
    def tags_list() -> str:
        """All tags"""
        return "tag:list:all"
    
    # ================================== COLORS & SIZES ==================================
    @staticmethod
    def colors_list() -> str:
        """All colors"""
        return "color:list:all"
    
    @staticmethod
    def sizes_list() -> str:
        """All sizes"""
        return "size:list:all"
    
    # ================================== WAREHOUSE ==================================
    @staticmethod
    def warehouse_list() -> str:
        """All warehouses"""
        return "warehouse:list:all"
    
    @staticmethod
    def warehouse_stock(warehouse_id: str) -> str:
        """Stock summary by warehouse"""
        return f"warehouse:stock_summary:{warehouse_id}"
    
    # ================================== HELPER METHODS ==================================
    @staticmethod
    def pattern_product_all() -> str:
        """Pattern để invalidate tất cả product cache"""
        return "product:*"
    
    @staticmethod
    def pattern_cart_user(user_id: str) -> str:
        """Pattern để invalidate tất cả cart cache của user"""
        return f"cart:*:{user_id}*"
    
    @staticmethod
    def pattern_stock_product(product_id: str) -> str:
        """Pattern để invalidate tất cả stock cache của product"""
        return f"stock:*:product:{product_id}*"
    
    @staticmethod
    def pattern_offer_all() -> str:
        """Pattern để invalidate tất cả offer cache"""
        return "offer:*"