from fastapi import APIRouter
from pydantic import BaseModel
from services.chat_service import handle_chat

router = APIRouter()

class ChatIn(BaseModel):
    message: str

@router.post("/api/chat")
async def chat_api(payload: ChatIn):
    return await handle_chat(payload.message)