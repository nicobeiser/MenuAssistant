from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from models.dish import Dish
from schemas.dish import DishBulkIn
from sqlalchemy.orm import Session
from metrics.db import get_db
from services.menu_service import (
    upload_images_service,
    list_images_service,
    get_image_file_service,
    delete_image_service,
    delete_all_images_service,
    build_menu_extraction_prompt,
    call_parser_from_upload,
    save_dishes as save_dishes_service,
    get_dishes as get_dishes_service
)
from sqlalchemy.ext.asyncio import AsyncSession

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


@router.post("/parse_image")
async def parse_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="La imagen está vacía")

    result = call_parser_from_upload(file.filename, image_bytes)
    return result


@router.post("/dishes/save")
async def save_dishes_endpoint(payload: DishBulkIn, db: AsyncSession = Depends(get_db)):
    return await save_dishes_service(payload, db)


@router.get("/dishes")
async def get_dishes(db: AsyncSession = Depends(get_db)):
    return await get_dishes_service(db)