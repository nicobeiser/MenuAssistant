from fastapi import APIRouter, UploadFile, File
from services.image_service import (
    upload_images_service,
    list_images_service,
    get_image_file_service,
    delete_image_service,
    delete_all_images_service
)

router = APIRouter()

@router.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    return await upload_images_service(files)


@router.get("/images")
def list_images():
    return list_images_service()


@router.get("/images/{filename}/file")
def get_image_file(filename: str):
    return get_image_file_service(filename)


@router.delete("/images/{filename}")
def delete_image(filename: str):
    return delete_image_service(filename)


@router.delete("/images")
def delete_all_images():
    return delete_all_images_service()