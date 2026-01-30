from google import genai
from google.genai import types
import requests

from pathlib import Path

image_path = Path(__file__).parent / "MyCar.jpg"

with open(image_path, "rb") as f:
    image_bytes = f.read()

image = types.Part.from_bytes(
    data=image_bytes,
    mime_type="image/jpeg"
)
client = genai.Client(api_key="")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        image,
        "Can you tell me what car is this?"
    ],
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())]
    ),
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    if part.executable_code is not None:
        print(part.executable_code.code)
    if part.code_execution_result is not None:
        print(part.code_execution_result.output)
    if part.as_image() is not None:
        with open("out.png", "wb") as f:
            f.write(part.as_image().image_bytes)
        print("Imagen guardada como out.png")
