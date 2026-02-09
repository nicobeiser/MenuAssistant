from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pathlib import Path
import shutil

from first import recieve_prompt
from load_image import IMAGES_DIR, ALLOWED_EXTENSIONS

BASE_DIR = Path(__file__).resolve().parent

# Ensure images directory exists
IMAGES_DIR.mkdir(exist_ok=True)

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
    reply = recieve_prompt(payload.message)
    return {"reply": reply}


@app.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    """Upload one or more menu images."""
    saved = []
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{ext}' not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}",
            )
        dest = IMAGES_DIR / f.filename
        with open(dest, "wb") as buf:
            shutil.copyfileobj(f.file, buf)
        saved.append(f.filename)
    return {"uploaded": saved}


@app.get("/images")
def list_images():
    """List all uploaded menu images."""
    if not IMAGES_DIR.exists():
        return {"images": []}
    files = [
        f.name for f in sorted(IMAGES_DIR.iterdir())
        if f.suffix.lower() in ALLOWED_EXTENSIONS
    ]
    return {"images": files}


@app.get("/images/{filename}/file")
def get_image_file(filename: str):
    """Serve an uploaded image file (for previews)."""
    path = IMAGES_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)


@app.delete("/images/{filename}")
def delete_image(filename: str):
    """Delete a specific uploaded image."""
    path = IMAGES_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    path.unlink()
    return {"deleted": filename}


@app.delete("/images")
def delete_all_images():
    """Delete all uploaded images."""
    if IMAGES_DIR.exists():
        for f in IMAGES_DIR.iterdir():
            if f.suffix.lower() in ALLOWED_EXTENSIONS:
                f.unlink()
    return {"status": "all images deleted"}
