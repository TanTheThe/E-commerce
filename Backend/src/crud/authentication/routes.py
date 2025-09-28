from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from starlette import status
from src.crud.authentication.services.change_password import ChangePasswordService
from src.crud.authentication.services.create_account import CreateAccountService
from src.crud.authentication.services.login import LoginService
from src.dependencies import AccessTokenBearer, RefreshTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.authentication.utils import create_access_token
from fastapi.responses import JSONResponse, RedirectResponse
from src.schemas.user import AdminStaffRole, ChangePasswordModel, UserCreateModel, UserLoginModel, LoginAdminModel, PasswordResetConfirmModel, PasswordResetEmailModel, UserRole, \
    VerifyOTPModel, VerifyLoginAdminModel, Setup2FA
from src.database.main import get_session
from datetime import datetime
from src.crud.authentication.services.services import AuthenticationService
from src.dependencies import admin_role_middleware, customer_role_middleware, staff_role_middleware

auth_admin_router = APIRouter(prefix="/auth")
auth_customer_router = APIRouter(prefix="/auth")
auth_staff_router = APIRouter(prefix="/auth")

REFRESH_TOKEN_EXPIRY = 2

auth_service = AuthenticationService()
access_token_bearer = AccessTokenBearer()
login_service = LoginService()
change_password_service = ChangePasswordService()
create_account_service = CreateAccountService()


@auth_customer_router.post("/login")
async def login_customer(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    return await login_service.login_customer_service(user_data, session)


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
async def forgot_password(email_data: PasswordResetEmailModel, session: AsyncSession = Depends(get_session)):
    message = await auth_service.forgot_password_service(email_data.email, email_data.check, UserRole.CUSTOMER, session)

    return JSONResponse(
        content={"message": message},
        status_code=status.HTTP_200_OK
    )


@auth_customer_router.post('/confirm-reset')
async def forget_password_confirm(data: PasswordResetConfirmModel,
                                  session: AsyncSession = Depends(get_session)):
    message = await auth_service.forgot_password_confirm_service(data, UserRole.CUSTOMER, session)
    return JSONResponse(
        content={"message": message},
        status_code=status.HTTP_200_OK
    )


@auth_customer_router.post("/forgot-password/verify-otp")
async def verify_otp(data: VerifyOTPModel, session: AsyncSession = Depends(get_session)):
    token = await auth_service.verify_otp(data, UserRole.CUSTOMER, session)

    return JSONResponse(
        content={
            "content": {
                "token": token
            }
        },
        status_code=status.HTTP_200_OK
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
async def change_password_customer(passwords: ChangePasswordModel, session: AsyncSession = Depends(get_session),
                                   token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    return await change_password_service.change_password(user_id, passwords, session)


@auth_customer_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, 
                              bg_tasks: BackgroundTasks,
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
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    try:
        await create_account_service.verify_user_account(token, UserRole.CUSTOMER, session)
        return RedirectResponse(url="http://{DOMAIN_CLIENT}/login?verified=true", status_code=302)
    except Exception:
        return RedirectResponse(url="http://{DOMAIN_CLIENT}/login?verified=false", status_code=302)



# ---------------------------------------------------- Admin ---------------------------------------------------------


@auth_admin_router.post("/login")
async def login_admin(user_data: LoginAdminModel, session: AsyncSession = Depends(get_session)):
    return await login_service.login_admin_staff(user_data, AdminStaffRole.ADMIN, session)


@auth_admin_router.post("/login/2fa")
async def login_admin_with_2fa(user_data: Setup2FA, session: AsyncSession = Depends(get_session)):
    return await login_service.setup_2fa(user_data, AdminStaffRole.ADMIN, session)


@auth_admin_router.post("/login/verify")
async def verify_login_admin(user_data: VerifyLoginAdminModel, session: AsyncSession = Depends(get_session)):
    return await login_service.verify_login(user_data, AdminStaffRole.ADMIN, session)


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
    message = await auth_service.forgot_password_service(email_data.email, email_data.check, UserRole.ADMIN, session)

    return JSONResponse(
        content={"message": message},
        status_code=status.HTTP_200_OK
    )


@auth_admin_router.post('/confirm-reset')
async def forget_password_confirm(data: PasswordResetConfirmModel,
                                  session: AsyncSession = Depends(get_session)):
    message = await auth_service.forgot_password_confirm_service(data, UserRole.ADMIN, session)
    return JSONResponse(content={"message": message}, status_code=200)


@auth_admin_router.post("/forgot-password/verify-otp")
async def verify_otp(data: VerifyOTPModel, session: AsyncSession = Depends(get_session)):
    token = await auth_service.verify_otp(data, UserRole.ADMIN, session)

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
    return await change_password_service.change_password(user_id, passwords, session)




# ---------------------------------------------------- Staff ---------------------------------------------------------


@auth_staff_router.post("/signup", status_code=status.HTTP_201_CREATED)
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
        return RedirectResponse(url="http://{DOMAIN_CLIENT}/login?verified=true", status_code=302)
    except Exception:
        return RedirectResponse(url="http://{DOMAIN_CLIENT}/login?verified=false", status_code=302)
    

@auth_staff_router.post("/login")
async def login_staff(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    return await login_service.login_admin_staff(user_data, AdminStaffRole.STAFF, session)


@auth_staff_router.post("/login/2fa")
async def login_admin_with_2fa(user_data: Setup2FA, session: AsyncSession = Depends(get_session)):
    return await login_service.setup_2fa(user_data, AdminStaffRole.STAFF, session)


@auth_staff_router.post("/login/verify")
async def verify_login_admin(user_data: VerifyLoginAdminModel, session: AsyncSession = Depends(get_session)):
    return await login_service.verify_login(user_data, AdminStaffRole.STAFF, session)


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

@auth_staff_router.post('/forgot-password')
async def forgot_password(email_data: PasswordResetEmailModel, session: AsyncSession = Depends(get_session)):
    message = await auth_service.forgot_password_service(email_data.email, email_data.check, UserRole.STAFF, session)

    return JSONResponse(
        content={"message": message},
        status_code=status.HTTP_200_OK
    )


@auth_staff_router.post('/confirm-reset')
async def forget_password_confirm(data: PasswordResetConfirmModel,
                                  session: AsyncSession = Depends(get_session)):
    message = await auth_service.forgot_password_confirm_service(data, UserRole.STAFF, session)
    return JSONResponse(content={"message": message}, status_code=200)


@auth_staff_router.post("/forgot-password/verify-otp")
async def verify_otp(data: VerifyOTPModel, session: AsyncSession = Depends(get_session)):
    token = await auth_service.verify_otp(data, UserRole.STAFF, session)

    return JSONResponse(
        content={
            "content": {
                "token": token
            }
        },
        status_code=status.HTTP_200_OK
    )
    
@auth_customer_router.put('/change-password', dependencies=[Depends(customer_role_middleware)])
async def change_password_customer(passwords: ChangePasswordModel, session: AsyncSession = Depends(get_session),
                                   token_details: dict = Depends(access_token_bearer)):
    user_id = token_details['user']['id']
    return await change_password_service.change_password(user_id, passwords, session)