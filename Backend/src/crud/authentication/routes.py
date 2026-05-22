from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from starlette import status
from src.config import Config
from src.crud.authentication.services.change_password import ChangePasswordService
from src.crud.authentication.services.create_account.create_account import CreateAccountService
from src.crud.authentication.services.detect_user_role import DetectUserRoleService
from src.crud.authentication.services.forgot_password.forgot_password import ForgotPasswordService
from src.crud.authentication.services.forgot_password.forgot_password_confirm import ForgotPasswordConfirmService
from src.crud.authentication.services.forgot_password.verify_otp import VerifyOtpService
from src.crud.authentication.services.login.login_admin_staff import LoginAdminStaffService
from src.crud.authentication.services.login.login_customer import LoginCustomerService
from src.crud.authentication.services.login_2fa.setup_2fa import Setup2FAService
from src.crud.authentication.services.login_2fa.verify_login import VerifyLoginService
from src.crud.authentication.services.logout.logout import LogoutService
from src.crud.authentication.services.verify_user_account.verify_user_account import VerifyUserAccountService
from src.dependencies import AccessTokenBearer, RefreshTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.authentication.utils import create_access_token
from fastapi.responses import JSONResponse, RedirectResponse
from src.schemas.user import AdminStaffRole, ChangePasswordModel, UserCreateModel, UserLoginModel, PasswordResetEmailModel, UserRole, \
    VerifyOTPModel, VerifyLoginAdminModel, Setup2FA, ForgotPasswordConfirmModel
from src.database.main import get_session
from datetime import datetime
from src.dependencies import admin_role_middleware, customer_role_middleware, staff_role_middleware

auth_admin_router = APIRouter(prefix="/auth")
auth_customer_router = APIRouter(prefix="/auth")
auth_staff_router = APIRouter(prefix="/auth")

REFRESH_TOKEN_EXPIRY = 2

access_token_bearer = AccessTokenBearer()
change_password_service = ChangePasswordService()
create_account_service = CreateAccountService()
login_customer_service = LoginCustomerService()
forgot_password_service = ForgotPasswordService()
forgot_password_confirm_service = ForgotPasswordConfirmService()
verify_otp_service = VerifyOtpService()
verify_user_account_service = VerifyUserAccountService()
login_admin_staff_service = LoginAdminStaffService()
setup_2fa_service = Setup2FAService()
verify_login_service = VerifyLoginService()
logout_service = LogoutService()
detect_user_role_service = DetectUserRoleService()


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


@auth_customer_router.get("/logout", dependencies=[Depends(customer_role_middleware)])
async def logout_customer(request: Request, token_details: dict = Depends(AccessTokenBearer()),
                       session: AsyncSession = Depends(get_session)):
    await logout_service.revoke_token(token_details, request, session, UserRole.CUSTOMER)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Đăng xuất thành công"
        }
    )


@auth_customer_router.post('/forgot-password')
async def forgot_password(request: Request, email_data: PasswordResetEmailModel, session: AsyncSession = Depends(get_session)):
    message = await forgot_password_service.forgot_password(email_data.email, email_data.check, UserRole.CUSTOMER, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message
        }
    )


@auth_customer_router.post('/confirm-reset')
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
async def change_password_customer(passwords: ChangePasswordModel, request: Request, session: AsyncSession = Depends(get_session),
                                   token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    result = await change_password_service.change_password(user_id, passwords, UserRole.CUSTOMER, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đổi mật khẩu {result['role_display']} thành công",
            "content": result["data"]
        }
    )


@auth_customer_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, 
                              bg_tasks: BackgroundTasks,
                              request: Request = None,
                              session: AsyncSession = Depends(get_session)):
    new_user = await create_account_service.create_user_account(user_data, UserRole.CUSTOMER, bg_tasks, session, request)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tạo tài khoản thành công! Vui lòng kiểm tra email để tiến hành xác thực",
            "content": new_user
        }
    )


@auth_customer_router.get('/verify/{token}')
async def verify_user_account(token: str, request: Request, session: AsyncSession = Depends(get_session)):
    try:
        await verify_user_account_service.verify_user_account(token, UserRole.CUSTOMER, request, session)
        return RedirectResponse(url=f"http://{Config.CUSTOMER_DOMAIN_CLIENT}/login?verified=true", status_code=302)
    except Exception:
        return RedirectResponse(url=f"http://{Config.CUSTOMER_DOMAIN_CLIENT}/login?verified=false", status_code=302)



# ---------------------------------------------------- Admin ---------------------------------------------------------


@auth_admin_router.post("/login")
async def login_admin(user_data: UserLoginModel, request: Request, session: AsyncSession = Depends(get_session)):
    allowed_roles = [AdminStaffRole.ADMIN, AdminStaffRole.STAFF]
    admin_staff_role = await detect_user_role_service.detect_user_role(user_data.email, allowed_roles, session)

    result = await login_admin_staff_service.login_admin_staff(user_data, admin_staff_role, request, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": result["message"],
            "content": result["data"]
        }
    )


@auth_admin_router.post("/login/2fa")
async def login_admin_with_2fa(user_data: Setup2FA, request: Request, session: AsyncSession = Depends(get_session)):
    allowed_roles = [AdminStaffRole.ADMIN, AdminStaffRole.STAFF]
    admin_staff_role = await detect_user_role_service.detect_role_from_token(user_data.token, allowed_roles, "first_class_login", session)

    result = await setup_2fa_service.setup_2fa(user_data, admin_staff_role, request, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": result["message"],
            "content": result["data"]
        }
    )


@auth_admin_router.post("/login/verify")
async def verify_login_admin(user_data: VerifyLoginAdminModel, request: Request, session: AsyncSession = Depends(get_session)):
    allowed_roles = [AdminStaffRole.ADMIN, AdminStaffRole.STAFF]
    admin_staff_role = await detect_user_role_service.detect_role_from_token(user_data.token, allowed_roles, "first_class_login", session)

    result = await verify_login_service.verify_login(user_data, admin_staff_role, request, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": result["message"],
            "content": result["data"]
        }
    )


@auth_admin_router.get("/logout", dependencies=[Depends(admin_role_middleware)])
async def logout_admin(request: Request, token_details: dict = Depends(AccessTokenBearer()),
                       session: AsyncSession = Depends(get_session)):
    await logout_service.revoke_token(token_details, request, session, UserRole.ADMIN)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Đăng xuất thành công"
        }
    )


@auth_admin_router.post('/forgot-password')
async def forgot_password(request: Request, email_data: PasswordResetEmailModel, session: AsyncSession = Depends(get_session)):
    allowed_roles = [AdminStaffRole.ADMIN, AdminStaffRole.STAFF]
    admin_staff_role = await detect_user_role_service.detect_user_role(email_data.email, allowed_roles, session)

    message = await forgot_password_service.forgot_password(email_data.email, email_data.check, admin_staff_role, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message
        }
    )


@auth_admin_router.post('/confirm-reset')
async def forget_password_confirm(data: ForgotPasswordConfirmModel,
                                  request: Request,
                                  session: AsyncSession = Depends(get_session)):
    allowed_roles = [AdminStaffRole.ADMIN, AdminStaffRole.STAFF]
    admin_staff_role = await detect_user_role_service.detect_role_from_token(data.token, allowed_roles,
                                                                             "reset_password", session)

    message = await forgot_password_confirm_service.forgot_password_confirm(data, admin_staff_role, session, request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message
        }
    )


@auth_admin_router.post("/forgot-password/verify-otp")
async def verify_otp(request: Request, data: VerifyOTPModel, session: AsyncSession = Depends(get_session)):
    allowed_roles = [AdminStaffRole.ADMIN, AdminStaffRole.STAFF]
    admin_staff_role = await detect_user_role_service.detect_user_role(data.email, allowed_roles, session)

    token = await verify_otp_service.verify_otp(data, admin_staff_role, session, request)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Token sau khi xác thực OTP thành công",
            "content": {
                "token": token
            }
        }
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
async def change_password_admin(request: Request, passwords: ChangePasswordModel, session: AsyncSession = Depends(get_session),
                                   token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    result = await change_password_service.change_password(user_id, passwords, UserRole.ADMIN, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đổi mật khẩu {result['role_display']} thành công",
            "content": result["data"]
        }
    )



# ---------------------------------------------------- Staff ---------------------------------------------------------


@auth_admin_router.post("/signup", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def create_user_account(user_data: UserCreateModel,
                              bg_tasks: BackgroundTasks,
                              request: Request = None,
                              session: AsyncSession = Depends(get_session)):
    new_user = await create_account_service.create_user_account(user_data, UserRole.STAFF, bg_tasks, session, request)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tạo tài khoản thành công! Vui lòng kiểm tra email để tiến hành xác thực",
            "content": new_user
        }
    )


@auth_staff_router.get('/verify/{token}')
async def verify_user_account(token: str, request: Request, session: AsyncSession = Depends(get_session)):
    try:
        await verify_user_account_service.verify_user_account(token, UserRole.STAFF, request, session)
        return RedirectResponse(url=f"http://{Config.ADMIN_DOMAIN_CLIENT}/staffs?verified=true", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"http://{Config.ADMIN_DOMAIN_CLIENT}/staffs?verified=false", status_code=302)


@auth_staff_router.get("/logout", dependencies=[Depends(staff_role_middleware)])
async def logout_staff(request: Request, token_details: dict = Depends(AccessTokenBearer()),
                       session: AsyncSession = Depends(get_session)):
    await logout_service.revoke_token(token_details, request, session, UserRole.STAFF)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Đăng xuất thành công"
        }
    )


@auth_staff_router.put('/change-password', dependencies=[Depends(staff_role_middleware)])
async def change_password_staff(request: Request, passwords: ChangePasswordModel, session: AsyncSession = Depends(get_session),
                                   token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    result = await change_password_service.change_password(user_id, passwords, UserRole.STAFF, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Đổi mật khẩu {result['role_display']} thành công",
            "content": result["data"]
        }
    )
