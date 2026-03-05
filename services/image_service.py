from pathlib import Path
import shutil
from fastapi import HTTPException
from metrics.service import track_event
from load_image import IMAGES_DIR, ALLOWED_EXTENSIONS
from fastapi.responses import FileResponse


async def upload_images_service(files):
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


def list_images_service():
    if not IMAGES_DIR.exists():
        return {"images": []}

    files = [
        f.name for f in sorted(IMAGES_DIR.iterdir())
        if f.suffix.lower() in ALLOWED_EXTENSIONS
    ]

    return {"images": files}


def get_image_file_service(filename):
    path = IMAGES_DIR / filename

    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(path)


def delete_image_service(filename):
    path = IMAGES_DIR / filename

    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    path.unlink()

    return {"deleted": filename}


def delete_all_images_service():
    if IMAGES_DIR.exists():
        for f in IMAGES_DIR.iterdir():
            if f.suffix.lower() in ALLOWED_EXTENSIONS:
                f.unlink()

    return {"status": "all images deleted"}