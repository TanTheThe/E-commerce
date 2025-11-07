from datetime import datetime, timedelta
from src.database.models import User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.schemas.user import UserCreateModel, UserRole
from src.crud.authentication.utils import create_url_safe_token, decode_url_safe_token, generate_password_hash
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

        condition = [User.email == email, User.deleted_at.is_(None)]
        user_exists = await user_repository.get_user(session=session, where_conditions=condition)

        if user_exists:
            if user_exists.is_verified:
                UserException.email_exists()
            if user_exists.created_at and (datetime.now() - user_exists.created_at) > timedelta(hours=24):
                condition_delete = [User.id == user_exists.id]
                await user_repository.delete_user(session=session, where_conditions=condition_delete)
            else:
                AuthException.email_already_registered()

        try:
            password_hash = generate_password_hash(user_data.password)
            user_create_data = {
                **user_data.model_dump(),
                "password": password_hash,
                'email': email,
                'is_verified': False,
                'created_at': datetime.now(),
            }

            if role == UserRole.CUSTOMER:
                user_create_data['is_customer'] = True
                user_create_data['customer_status'] = "active"
            elif role == UserRole.STAFF:
                user_create_data['is_staff'] = True
                user_create_data['staff_status'] = "active"

            new_user = await user_repository.create_user(user_create_data, session)
            await session.commit()

        except Exception as e:
            await session.rollback()
            raise AuthException.creation_failed()

        token_payload = {
            "email": email,
            "user_id": str(new_user.id),
            "timestamp": datetime.now().isoformat()
        }

        token = create_url_safe_token(
            token_payload,
            role.value,
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
