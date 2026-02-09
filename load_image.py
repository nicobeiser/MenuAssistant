from google.genai import types


def load_image(path: str):
    with open(path, "rb") as f:
        return types.Part.from_bytes(
            data=f.read(),
            mime_type="image/png"
        )