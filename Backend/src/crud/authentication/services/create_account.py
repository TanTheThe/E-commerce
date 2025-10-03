from datetime import datetime
from src.database.models import User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.schemas.user import UserCreateModel, UserRole
from src.crud.authentication.utils import create_url_safe_token, decode_url_safe_token
from sqlmodel import and_
from src.mail import create_message, mail
from fastapi import BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from src.config import Config
from src.crud.user.repositories import UserRepository

user_repository = UserRepository()


class CreateAccountService:
    async def create_user_account(self, user_data: UserCreateModel, role: UserRole,
                                  bg_tasks: BackgroundTasks, session: AsyncSession):
        email = user_data.email

        condition = and_(User.email == email)
        user_exists = await user_repository.get_user(condition, session)
        if user_exists:
            UserException.email_exists()

        try:
            new_user = await user_repository.create_user(user_data, role, session)
        except Exception as e:
            raise AuthException.creation_failed()

        token = create_url_safe_token(
            {"email": email}, 
            role=role.value, 
            purpose="create_account"
        )
        
        link = f"http://{Config.DOMAIN}/api/v1/{role.value}/auth/verify/{token}"
        
        subject, html = self.create_verification_email_content(link, role)
        
        message = create_message(
            recipients=[email],
            subject=subject,
            body=html
        )
        
        bg_tasks.add_task(mail.send_message, message)

        return {
            "id": str(new_user.id), 
            "email": new_user.email, 
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "role": role.value
        }
        
    def create_verification_email_content(self, link: str, role: UserRole):
        if role == UserRole.CUSTOMER:
            subject = "Xác thực tài khoản khách hàng"
            role_text = "khách hàng"
        else:
            subject = "Xác thực tài khoản nhân viên"
            role_text = "nhân viên"
            
        html = f"""
        <h1>Xác thực email</h1>
        <p>Chào bạn,</p>
        <p>Cảm ơn bạn đã đăng ký tài khoản {role_text}.</p>
        <p>Vui lòng nhấp vào đường link sau để xác thực email của bạn:</p>
        <p><a href="{link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Xác thực email</a></p>
        <p>Hoặc copy và paste link sau vào trình duyệt:</p>
        <p>{link}</p>
        <p>Link này sẽ hết hạn sau 24 giờ.</p>
        <p>Trân trọng,<br>Đội ngũ hỗ trợ</p>
        """
        
        return subject, html

    async def verify_user_account(self, token: str, role: UserRole, session: AsyncSession):
        token_data = decode_url_safe_token(
            token,
            role=role.value,
            purpose="create_account"
        )
            
        if token_data is None:
            AuthException.authentication_error()

        user_email = token_data.get('email')
        if not user_email:
            AuthException.authentication_error()
            
        condition = and_(User.email == user_email)
        user = await user_repository.get_user(condition, session)

        if not user:
            AuthException.user_not_found()
            
        update_data = {'is_verified': True, 'updated_at': datetime.now()}
        
        if role == UserRole.CUSTOMER:
            update_data['is_customer'] = True
        elif role == UserRole.STAFF:
            update_data['is_staff'] = True
            
        try:
            condition = and_(User.id == user.id, User.deleted_at.is_(None))
            await user_repository.update_user_some_field(condition, update_data, session)
            await session.commit()

        except Exception as e:
            raise AuthException.verification_failed()
            
        return True
