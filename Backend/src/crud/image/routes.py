from fastapi import APIRouter, status, Depends, UploadFile, File, Form
from src.crud.image.services.upload_image import UploadImageService
from src.dependencies import AccessTokenBearer, admin_role_middleware
from fastapi.responses import JSONResponse
from src.schemas.image import ImageUploadModel, UploadType

image_admin_router = APIRouter(prefix="/image")
image_customer_router = APIRouter(prefix="/image")
image_staff_router = APIRouter(prefix="/image")

upload_image_service = UploadImageService()

access_token_bearer = AccessTokenBearer()


@image_admin_router.post("/upload", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role_middleware)])
async def upload_image(file: UploadFile = File(...),
                       type: UploadType = Form(...),
                       slug: str = Form(...),
                       token_details: dict = Depends(access_token_bearer)):
    upload_data = ImageUploadModel(type=type, slug=slug)

    result = await upload_image_service.upload_image(file, upload_data)

    await file.close()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Upload ảnh thành công",
            "content": result
        }
    )


