from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from metrics.db import get_db
from schemas.dish import DishCreateIn, DishUpdateIn
from services.menu_service import create_dish, update_dish, get_dishes, delete_dish

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = BASE_DIR / "tests" / "testParser"

router = APIRouter(prefix="/dishes", tags=["dishes"])

@router.get("/parser")
def serve_parser():
    return FileResponse(TEST_DIR / "testParser.html")

@router.get("/page")
def serve_dishes_page():
    return FileResponse(TEST_DIR / "Dishes" / "Dishes.html")

@router.get("/api")
async def get_all_dishes(db: AsyncSession = Depends(get_db)):
    return await get_dishes(db)

@router.post("/api")
async def create_dish_endpoint(
    payload: DishCreateIn,
    db: AsyncSession = Depends(get_db)
):
    return await create_dish(payload, db)

@router.put("/api/{dish_id}")
async def update_dish_endpoint(
    dish_id: int,
    payload: DishUpdateIn,
    db: AsyncSession = Depends(get_db)
):
    return await update_dish(dish_id, payload, db)

@router.delete("/api/{dish_id}")
async def delete_dish_endpoint(
    dish_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await delete_dish(dish_id, db)