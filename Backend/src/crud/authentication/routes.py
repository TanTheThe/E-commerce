from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette import status
from src.config import Config
from src.crud.authentication.services.change_password import ChangePasswordService
from src.crud.authentication.services.create_account import CreateAccountService
from src.crud.authentication.services.forgot_password import ForgotPasswordService
from src.crud.authentication.services.forgot_password_confirm import ForgotPasswordConfirmService
from src.crud.authentication.services.login import LoginService
from src.crud.authentication.services.login_admin_staff import LoginAdminStaffService
from src.crud.authentication.services.login_customer import LoginCustomerService
from src.crud.authentication.services.verify_otp import VerifyOtpService
from src.crud.authentication.services.verify_user_account import VerifyUserAccountService
from src.dependencies import AccessTokenBearer, RefreshTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.authentication.utils import create_access_token
from fastapi.responses import JSONResponse, RedirectResponse
from src.schemas.user import AdminStaffRole, ChangePasswordModel, UserCreateModel, UserLoginModel, PasswordResetEmailModel, UserRole, \
    VerifyOTPModel, VerifyLoginAdminModel, Setup2FA, ForgotPasswordConfirmModel
from src.database.main import get_session
from datetime import datetime
from src.crud.authentication.services.services import AuthenticationService
from src.dependencies import admin_role_middleware, customer_role_middleware, staff_role_middleware

auth_admin_router = APIRouter(prefix="/auth")
auth_customer_router = APIRouter(prefix="/auth")
auth_staff_router = APIRouter(prefix="/auth")

limiter = Limiter(key_func=get_remote_address)

REFRESH_TOKEN_EXPIRY = 2

auth_service = AuthenticationService()
access_token_bearer = AccessTokenBearer()
login_service = LoginService()
change_password_service = ChangePasswordService()
create_account_service = CreateAccountService()
login_customer_service = LoginCustomerService()
forgot_password_service = ForgotPasswordService()
forgot_password_confirm_service = ForgotPasswordConfirmService()
verify_otp_service = VerifyOtpService()
verify_user_account_service = VerifyUserAccountService()
login_admin_staff_service = LoginAdminStaffService()


@auth_customer_router.post("/login")
async def login_customer(request: Request, user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    login_data = await login_customer_service.login_customer(user_data, request, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Đăng nhập thành công",
            "content": login_data
        }
    )


# @auth_customer_router.get("/logout", dependencies=[Depends(customer_role_middleware)])
# async def revoke_token(request: Request, token_details: dict = Depends(AccessTokenBearer())):
#     await auth_service.revoke_token_service(token_details, request)
#
#     return JSONResponse(
#         content={
#             "message": "Đăng xuất thành công"
#         },
#         status_code=status.HTTP_200_OK
#     )


@auth_customer_router.post('/forgot-password')
@limiter.limit("3/minute")
async def forgot_password(email_data: PasswordResetEmailModel, session: AsyncSession = Depends(get_session)):
    message = await forgot_password_service.forgot_password(email_data.email, email_data.check, UserRole.CUSTOMER, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message
        }
    )


@auth_customer_router.post('/confirm-reset')
@limiter.limit("5/minute")
async def forget_password_confirm(data: ForgotPasswordConfirmModel,
                                  request: Request,
                                  session: AsyncSession = Depends(get_session)):
    message = await forgot_password_confirm_service.forgot_password_confirm(data, UserRole.CUSTOMER, session, request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message
        }
    )


@auth_customer_router.post("/forgot-password/verify-otp")
@limiter.limit("5/minute")
@limiter.limit("10/hour")
async def verify_otp(request: Request, data: VerifyOTPModel, session: AsyncSession = Depends(get_session)):
    token = await verify_otp_service.verify_otp(data, UserRole.CUSTOMER, session, request)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Token sau khi xác thực OTP thành công",
            "content": {
                "token": token
            }
        }
    )
    
    
@auth_customer_router.get('/refresh-token', dependencies=[Depends(customer_role_middleware)])
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now() and token_details['role'] == "customer":
        new_access_token = create_access_token(
            user_data=token_details["user"],
            role="customer"
        )

        return JSONResponse(
            content={
                "content": {
                    "access_token": new_access_token
                }
            }
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "message": "Token không hợp lệ hoặc đã hết hạn",
            "error_code": "auth_014",
        },
    )


@auth_customer_router.put('/change-password', dependencies=[Depends(customer_role_middleware)])
@limiter.limit("5/minute")
async def change_password_customer(passwords: ChangePasswordModel, session: AsyncSession = Depends(get_session),
                                   token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    role_display, result = await change_password_service.change_password(user_id, passwords, UserRole.CUSTOMER, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đổi mật khẩu {role_display} thành công",
            "content": {
                "user_id": result.get("user_id"),
                "email": result.get("email"),
                "updated_at": result.get("updated_at")
            }
        }
    )


@auth_customer_router.post("/signup", status_code=status.HTTP_201_CREATED)
@limiter.limit("6/hour")
async def create_user_account(user_data: UserCreateModel, 
                              bg_tasks: BackgroundTasks,
                              request: Request = None,
                              session: AsyncSession = Depends(get_session)):
    new_user = await create_account_service.create_user_account(user_data, UserRole.CUSTOMER, bg_tasks, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tạo tài khoản thành công! Vui lòng kiểm tra email để tiến hành xác thực",
            "content": new_user
        }
    )


@auth_customer_router.get('/verify/{token}')
@limiter.limit("6/hour")
async def verify_user_account(token: str, request: Request, session: AsyncSession = Depends(get_session)):
    try:
        await verify_user_account_service.verify_user_account(token, UserRole.CUSTOMER, request, session)
        return RedirectResponse(url=f"http://{Config.CUSTOMER_DOMAIN_CLIENT}/login?verified=true", status_code=302)
    except Exception:
        return RedirectResponse(url=f"http://{Config.CUSTOMER_DOMAIN_CLIENT}/login?verified=false", status_code=302)



# ---------------------------------------------------- Admin ---------------------------------------------------------


@auth_admin_router.post("/login")
async def login_admin(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    allowed_roles = [UserRole.ADMIN, UserRole.STAFF]
    admin_staff_role = await login_admin_staff_service.detect_user_role(user_data.email, allowed_roles, session)

    return await login_service.login_admin_staff(user_data, admin_staff_role, session)


@auth_admin_router.post("/login/2fa")
async def login_admin_with_2fa(user_data: Setup2FA, session: AsyncSession = Depends(get_session)):
    detected_role = await auth_service.detect_role_from_token(
        user_data.token,
        [UserRole.ADMIN, UserRole.STAFF],
        purpose="first_class_login"
    )

    admin_staff_role = AdminStaffRole.ADMIN if detected_role == UserRole.ADMIN else AdminStaffRole.STAFF

    return await login_service.setup_2fa(user_data, admin_staff_role, session)


@auth_admin_router.post("/login/verify")
async def verify_login_admin(user_data: VerifyLoginAdminModel, session: AsyncSession = Depends(get_session)):
    detected_role = await auth_service.detect_role_from_token(
        user_data.token,
        [UserRole.ADMIN, UserRole.STAFF],
        purpose="first_class_login"
    )

    admin_staff_role = AdminStaffRole.ADMIN if detected_role == UserRole.ADMIN else AdminStaffRole.STAFF

    return await login_service.verify_login(user_data, admin_staff_role, session)


# @auth_admin_router.get("/logout", dependencies=[Depends(admin_role_middleware)])
# async def revoke_token(request: Request, token_details: dict = Depends(AccessTokenBearer())):
#     await auth_service.revoke_token_service(token_details, request)
#
#     return JSONResponse(
#         content={
#             "message": "Đăng xuất thành công"
#         },
#         status_code=status.HTTP_200_OK
#     )


@auth_admin_router.post('/forgot-password')
async def forgot_password(email_data: PasswordResetEmailModel, session: AsyncSession = Depends(get_session)):
    detected_role = await auth_service.detect_user_role(
        email_data.email,
        [UserRole.ADMIN, UserRole.STAFF],
        session
    )

    message = await auth_service.forgot_password_service(email_data.email, email_data.check, detected_role, session)

    return JSONResponse(
        content={"message": message},
        status_code=status.HTTP_200_OK
    )


@auth_admin_router.post('/confirm-reset')
async def forgot_password_confirm(data: ForgotPasswordConfirmModel,
                                  session: AsyncSession = Depends(get_session)):
    detected_role = await auth_service.detect_role_from_token(
        data.token,
        [UserRole.ADMIN, UserRole.STAFF],
        purpose="reset_password"
    )

    message = await auth_service.forgot_password_confirm_service(data, detected_role, session)

    return JSONResponse(content={"message": message}, status_code=200)


@auth_admin_router.post("/forgot-password/verify-otp")
async def verify_otp(data: VerifyOTPModel, session: AsyncSession = Depends(get_session)):
    detected_role = await auth_service.detect_user_role(
        data.email,
        [UserRole.ADMIN, UserRole.STAFF],
        session
    )

    token = await auth_service.verify_otp(data, detected_role, session)

    return JSONResponse(
        content={
            "content": {
                "token": token
            }
        },
        status_code=status.HTTP_200_OK
    )


@auth_admin_router.get('/refresh-token', dependencies=[Depends(admin_role_middleware)])
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now() and token_details['role'] == "admin":
        new_access_token = create_access_token(
            user_data=token_details["user"],
            role="admin"
        )

        return JSONResponse(
            content={
                "content": {
                    "access_token": new_access_token
                }
            }
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "message": "Token không hợp lệ hoặc đã hết hạn",
            "error_code": "auth_014",
        },
    )
    
@auth_admin_router.put('/change-password', dependencies=[Depends(admin_role_middleware)])
async def change_password_admin(passwords: ChangePasswordModel, session: AsyncSession = Depends(get_session),
                                token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    return await change_password_service.change_password(user_id, passwords, UserRole.ADMIN, session)




# ---------------------------------------------------- Staff ---------------------------------------------------------


@auth_admin_router.post("/signup", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_user_account(user_data: UserCreateModel, 
                              bg_tasks: BackgroundTasks,
                              session: AsyncSession = Depends(get_session)):
    new_user = await create_account_service.create_user_account(user_data, UserRole.STAFF, bg_tasks, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tạo tài khoản thành công! Vui lòng kiểm tra email để tiến hành xác thực",
            "content": new_user
        }
    )


@auth_staff_router.get('/verify/{token}')
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    try:
        await create_account_service.verify_user_account(token, UserRole.STAFF, session)
        return RedirectResponse(url=f"http://{Config.ADMIN_DOMAIN_CLIENT}/staffs?verified=true", status_code=302)
    except Exception:
        return RedirectResponse(url=f"http://{Config.ADMIN_DOMAIN_CLIENT}/staffs?verified=false", status_code=302)


# @auth_staff_router.get("/logout", dependencies=[Depends(staff_role_middleware)])
# async def revoke_token(request: Request, token_details: dict = Depends(AccessTokenBearer())):
#     await auth_service.revoke_token_service(token_details, request)
#
#     return JSONResponse(
#         content={
#             "message": "Đăng xuất thành công"
#         },
#         status_code=status.HTTP_200_OK
#     )

    
@auth_staff_router.put('/change-password', dependencies=[Depends(staff_role_middleware)])
async def change_password_staff(passwords: ChangePasswordModel, session: AsyncSession = Depends(get_session),
                                   token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    return await change_password_service.change_password(user_id, passwords, UserRole.STAFF, session)