from google.genai import types
from pathlib import Path

MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

ALLOWED_EXTENSIONS = set(MIME_TYPES.keys())

IMAGES_DIR = Path(__file__).parent / "images"


def get_mime_type(path: str | Path) -> str:
    ext = Path(path).suffix.lower()
    return MIME_TYPES.get(ext, "application/octet-stream")


def load_image(path: str | Path) -> types.Part:
    path = Path(path)
    with open(path, "rb") as f:
        return types.Part.from_bytes(
            data=f.read(),
            mime_type=get_mime_type(path),
        )


def load_all_images() -> list[types.Part]:
    """Load all images from the images/ folder."""
    images = []
    if not IMAGES_DIR.exists():
        return images
    for file in sorted(IMAGES_DIR.iterdir()):
        if file.suffix.lower() in ALLOWED_EXTENSIONS:
            images.append(load_image(file))
    return images