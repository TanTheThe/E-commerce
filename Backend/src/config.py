from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URI: str
    JWT_SECRET_CUSTOMER: str
    JWT_SECRET_ADMIN: str
    JWT_SECRET_STAFF: str

    JWT_RESET_PASSWORD_SECRET_CUSTOMER: str
    JWT_RESET_PASSWORD_SECRET_ADMIN: str
    JWT_RESET_PASSWORD_SECRET_STAFF: str

    JWT_FIRST_CLASS_LOGIN_SECRET_ADMIN: str
    JWT_FIRST_CLASS_LOGIN_SECRET_STAFF: str

    JWT_CREATE_ACCOUNT_SECRET_CUSTOMER: str
    JWT_CREATE_ACCOUNT_SECRET_STAFF: str

    JWT_VERIFY_OTP_LOGIN_SECRET_ADMIN: str
    JWT_VERIFY_OTP_LOGIN_SECRET_STAFF: str

    JWT_ALGORITHM: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_MAX_CONNECTIONS: int = 50

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    CACHE_TTL_SHORT: int = 300          # 5 phút
    CACHE_TTL_MEDIUM: int = 1800        # 30 phút
    CACHE_TTL_LONG: int = 3600          # 1 giờ
    CACHE_TTL_VERY_LONG: int = 86400    # 24 giờ

    RATE_LIMIT_LOGIN_MAX: int = 5       # Max login attempts
    RATE_LIMIT_LOGIN_WINDOW: int = 300  # 5 phút
    RATE_LIMIT_OTP_MAX: int = 3         # Max OTP requests
    RATE_LIMIT_OTP_WINDOW: int = 900    # 15 phút

    JWT_BLACKLIST_ENABLED: bool = True
    JWT_BLACKLIST_TOKEN_CHECKS: list = ["access", "refresh"]

    DOMAIN: str
    CUSTOMER_DOMAIN_CLIENT: str
    ADMIN_DOMAIN_CLIENT: str

    ENVIRONMENT: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    VNPAY_TMN_CODE: str
    VNPAY_HASH_SECRET_KEY: str
    VNPAY_PAYMENT_URL: str
    VNPAY_RETURN_URL: str
    VNPAY_API_URL: str

    SUPABASE_URL: str
    SUPABASE_KEY: str
    BUCKET_NAME: str

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:8000,http://127.0.0.1:8000"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    
    @property
    def redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_hosts(self) -> list[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    model_config = SettingsConfigDict(
        env_file='../.env',
        extra='ignore'
    )


Config = Settings()
