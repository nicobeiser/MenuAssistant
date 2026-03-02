from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pathlib import Path
from metrics.router import router as metrics_router
import shutil
from metrics.db import engine, Base
from metrics.middleware import MetricsMiddleware
from first import recieve_prompt
from load_image import IMAGES_DIR, ALLOWED_EXTENSIONS
from metrics.service import track_event
import time
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from metrics.db import engine, Base
from metrics.timer import span
from fastapi.concurrency import run_in_threadpool

BASE_DIR = Path(__file__).resolve().parent

# Ensure images directory exists
IMAGES_DIR.mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown (si después querés cerrar conexiones, etc.)
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


DASH_DIR = BASE_DIR / "frontend" / "dashboard"

# Sirve los archivos estáticos (js/css/etc)
app.mount("/dashboard/static", StaticFiles(directory=str(DASH_DIR)), name="dashboard-static")

# Sirve el HTML principal
@app.get("/dashboard")
def dashboard():
    return FileResponse(DASH_DIR / "dashboard.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware)


class ChatIn(BaseModel):
    message: str


@app.post("/chat")
async def chat(payload: ChatIn):

    with span() as total:
        result = await run_in_threadpool(recieve_prompt, payload.message)

    total_ms = total["ms"]

    if isinstance(result, dict) and "text" in result and "metrics" in result:
        m = result["metrics"] or {}
        model_ms = m.get("model_latency_ms")

        await track_event(
            type="chat",
            total_ms=float(total_ms),
            model_ms=float(model_ms) if model_ms else None,
            meta=(
                f"ok={m.get('ok')};"
                f"images={m.get('images_count')};"
                f"prompt_chars={m.get('prompt_chars')}"
            )
        )

        return {"reply": result["text"]}

    await track_event(
        type="chat",
        total_ms=float(total_ms),
        model_ms=None,
        meta="fallback=true"
    )

    return {"reply": str(result)}


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

    await track_event(type="upload", meta=f"count={len(saved)}")
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









app.include_router(metrics_router)
