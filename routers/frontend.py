from fastapi import APIRouter
from fastapi.responses import FileResponse
from core.config import FRONTEND_DIR, DASHBOARD_DIR

router = APIRouter()

@router.get("/chat")
def chat_page():
    return FileResponse(FRONTEND_DIR / "chat.html")

@router.get("/dashboard")
def dashboard_page():
    return FileResponse(DASHBOARD_DIR / "dashboard.html")