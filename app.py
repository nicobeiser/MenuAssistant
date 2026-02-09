from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from first import recieve_prompt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatIn(BaseModel):
    message: str

@app.post("/chat")
def chat(payload: ChatIn):
    print("Mensaje recibido:", payload.message)


    reply = recieve_prompt(payload.message)

    print("Reply generado:", reply)
    return {"reply": reply}
