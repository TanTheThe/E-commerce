from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
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

    model_config = SettingsConfigDict(
        env_file='../.env',
        extra='ignore'
    )


Config = Settings()
