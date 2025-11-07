import hashlib
from datetime import datetime
from typing import Literal, Optional
from fastapi import Request
from src.crud.authentication.utils import TOKEN_CONFIG
import logging
import json

RoleType = Literal["customer", "admin", "staff"]
PurposeType = Literal["reset_password", "first_class_login", "verify_otp", "create_account"]

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

        ("customer", "create_account"): "customer:create_account:",
        ("staff", "create_account"): "staff:create_account:",
    }

    def get_redis(self, request: Request):
        return request.app.state.redis

    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def get_prefix(self, role: RoleType, purpose: PurposeType) -> str:
        prefix = self.PREFIX_MAP.get((role, purpose))
        if not prefix:
            raise ValueError(
                f"Invalid token combination: role='{role}', purpose='{purpose}'. "
                f"Valid combinations: {list(self.PREFIX_MAP.keys())}"
            )
        return prefix

    def build_key(self, identifier: str, prefix: str):
        return f"blacklist:{prefix}{identifier}"

    async def add_jwt_to_blocklist(self, jti: str, request: Request, ttl: int = 3600, metadata: Optional[dict] = None):
        try:
            redis = self.get_redis(request)
            key = self.build_key(jti, prefix=self.PREFIX_JWT)

            value = {
                "blacklisted_at": datetime.now().isoformat(),
                "type": "jwt",
                **(metadata or {}),
            }

            await redis.set(key, json.dumps(value), ex=ttl)
            return True

        except Exception as e:
            return False

    async def jwt_in_blocklist(self, jti: str, request: Request):
        try:
            redis = self.get_redis(request)
            key = self.build_key(jti, prefix=self.PREFIX_JWT)
            exists = await redis.exists(key)
            return exists == 1
        except Exception as e:
            logging.error(f"Error checking JWT blocklist for jti={jti}: {str(e)}")
            return False

    async def add_token_to_blocklist(self, token: str, role: RoleType, purpose: PurposeType, request: Request,
                                     ttl: Optional[int] = None, metadata: Optional[dict] = None):
        try:
            redis = self.get_redis(request)
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
            return True
        except ValueError as e:
            return False
        except Exception as e:
            return False


    async def token_in_blocklist(self, token: str, role: RoleType, purpose: PurposeType, request: Request):
        try:
            redis = self.get_redis(request)
            token_hash = self.hash_token(token)
            prefix = self.get_prefix(role, purpose)
            key = self.build_key(token_hash, prefix=prefix)
            exists = await redis.exists(key)
            return exists == 1
        except ValueError as e:
            return False
        except Exception as e:
            return False































