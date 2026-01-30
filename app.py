from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mock import mock_ai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # después lo ajustás
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatIn(BaseModel):
    message: str

@app.post("/chat")
def chat(payload: ChatIn):
    print("Mensaje recibido:", payload.message)
    reply = mock_ai(payload.message)
    print("Reply generado:", reply)
    return {"reply": reply}
