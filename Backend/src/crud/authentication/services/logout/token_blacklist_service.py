import hashlib
from datetime import datetime
from typing import Literal, Optional
from src.crud.authentication.utils import TOKEN_CONFIG
from src.cache.redis_manager import RedisManager
from src.cache.cache_service import CacheService
import logging
import json


RoleType = Literal["customer", "admin", "staff"]
PurposeType = Literal["reset_password", "first_class_login", "verify_otp", "create_account"]

logger = logging.getLogger(__name__)

redis_manager = RedisManager()
cache_service = CacheService()

class TokenBlacklistService:
    PREFIX_JWT = "jwt:"
    
    PREFIX_MAP = {
        ("customer", "reset_password"): "customer:reset_pwd:",
        ("admin", "reset_password"): "admin:reset_pwd:",
        ("staff", "reset_password"): "staff:reset_pwd:",
        
        ("admin", "first_class_login"): "admin:first_login:",
        ("staff", "first_class_login"): "staff:first_login:",
        
        ("admin", "verify_otp"): "admin:verify_otp:",
        ("staff", "verify_otp"): "staff:verify_otp:",
        ("customer", "verify_otp"): "customer:verify_otp:",
        
        ("customer", "create_account"): "customer:create_account:",
        ("staff", "create_account"): "staff:create_account:",
    }


    # ===================================== JWT BLACKLIST ==========================================
    
    async def add_jwt_to_blocklist(self, jti: str, ttl: int = 3600, metadata: Optional[dict] = None):
        try:
            redis = redis_manager.redis
            key = self.build_key(jti, prefix=self.PREFIX_JWT)

            value = {
                "blacklisted_at": datetime.now().isoformat(),
                "type": "jwt",
                **(metadata or {}),
            }

            await redis.set(key, json.dumps(value), ex=ttl)
            logger.info(f"JWT đã được thêm vào blacklist: jti={jti}, ttl={ttl}")
            return True

        except Exception as e:
            logger.error(f"Lỗi khi thêm JWT vào blocklist: {str(e)}")
            return False


    async def jwt_in_blocklist(self, jti: str):
        try:
            redis = redis_manager.redis
            key = self.build_key(jti, prefix=self.PREFIX_JWT)
            exists = await redis.exists(key)
            return exists == 1
        
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra JWT blocklist cho jti={jti}: {str(e)}")
            return False

    
    
    # ================================= URL-SAFE TOKEN BLACKLIST ============================================

    async def add_token_to_blocklist(self, token: str, role: RoleType, purpose: PurposeType,
                                     ttl: Optional[int] = None, metadata: Optional[dict] = None):
        try:
            redis = redis_manager.redis

            token_hash = self.hash_token(token)

            prefix = self.get_prefix(role, purpose)

            key = self.build_key(token_hash, prefix=prefix)

            if ttl is None:
                config = TOKEN_CONFIG.get((role, purpose))
                ttl = config.get("max_age", 3600) if config else 3600

            value = {
                "blacklisted_at": datetime.now().isoformat(),
                "type": "url_safe_token",
                "role": role,
                "purpose": purpose,
                **(metadata or {}),
            }

            await redis.set(key, json.dumps(value), ex=ttl)

            logger.info(f"Token đã được thêm vào blacklist: role={role}, purpose={purpose}, ttl={ttl}")
            return True

        except Exception as e:
            logger.error(f"Lỗi khi thêm token vào blocklist: {str(e)}")
            return False


    async def token_in_blocklist(self, token: str, role: RoleType, purpose: PurposeType):
        try:
            redis = redis_manager.redis
            token_hash = self.hash_token(token)
            prefix = self.get_prefix(role, purpose)
            key = self.build_key(token_hash, prefix=prefix)
            exists = await redis.exists(key)
            return exists == 1

        except Exception as e:
            logger.error(f"Lỗi khi check token trong blocklist: {str(e)}")
            return False




    def hash_token(self, token: str):
        return hashlib.sha256(token.encode()).hexdigest()
    
    def get_prefix(self, role: RoleType, purpose: PurposeType):
        prefix = self.PREFIX_MAP.get((role, purpose))
        
        if not prefix:
            valid_combinations = list(self.PREFIX_MAP.keys())
            raise ValueError(
                f"Token combination không hợp lệ: role='{role}', purpose='{purpose}'. "
                f"combinations hợp lệ: {valid_combinations}"
            )
        
        return prefix
    
    def build_key(self, identifier: str, prefix: str):
        return f"blacklist:{prefix}{identifier}"





























