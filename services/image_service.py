from pathlib import Path
import shutil
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from metrics.service import track_event
from load_image import IMAGES_DIR, ALLOWED_EXTENSIONS
from fastapi.responses import FileResponse
from first import receive_image_prompt
from metrics.db import get_db
from models.dish import Dish
from schemas.dish import DishBulkIn
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


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



def build_menu_extraction_prompt(image_url: str) -> str:
    return f"""
        You are an expert system for extracting structured restaurant menu data from images.

        Analyze the provided menu image carefully and extract every visible dish into valid JSON.

        Return ONLY raw JSON.
        Do not include markdown.
        Do not include explanations.
        Do not include comments.
        Do not wrap the response in ```json.

        The output must follow exactly this structure:

        {{
        "dishes": [
            {{
            "name": "string",
            "description": "string",
            "price": 0,
            "category": "string",
            "image_url": "{image_url}",
            "available": true,
            "tags": [],
            "extraction_confidence": 0.0,
            "extraction_source": "ai_import"
            }}
        ]
        }}

        Rules:
        1. Extract only dishes that are actually visible in the image.
        2. Do not invent dishes, categories, descriptions, or prices.
        3. Keep the original language exactly as written in the menu.
        4. If a dish has no description, use an empty string: "".
        5. If a category is not clearly visible, use "Sin categoría".
        6. If a price is not clearly readable, use null.
        7. "price" must be a number only, with no currency symbols or text.
        8. "available" must always be true by default.
        9. "tags" must be an empty array unless the image explicitly indicates something like vegan, spicy, gluten free, vegetarian, etc.
        10. "extraction_confidence" must be a number between 0.0 and 1.0 based on how certain you are about that dish's extracted fields.
        11. "extraction_source" must always be "ai_import".
        12. If the same dish appears multiple times, include it only once unless the price or description is clearly different.
        13. Ignore decorative text, restaurant slogans, addresses, phone numbers, and social media unless they are part of a dish.
        14. If the menu has sections like Burgers, Drinks, Desserts, use those as category values.
        15. Return one JSON object only.

        Example output:

        {{
        "dishes": [
            {{
            "name": "Hamburguesa Clásica",
            "description": "Carne, queso, lechuga y tomate",
            "price": 12000,
            "category": "Hamburguesas",
            "image_url": "{image_url}",
            "available": true,
            "tags": [],
            "extraction_confidence": 0.94,
            "extraction_source": "ai_import"
            }},
            {{
            "name": "Papas Fritas",
            "description": "",
            "price": 5000,
            "category": "Acompañamientos",
            "image_url": "{image_url}",
            "available": true,
            "tags": [],
            "extraction_confidence": 0.89,
            "extraction_source": "ai_import"
            }}
        ]
        }}
        """


def call_parser(filename: str):
    image_path = IMAGES_DIR / filename

   
    if not image_path.exists():
        print("error!!")
        return {"error": f"Image not found: {filename}"}


    with open(image_path, "rb") as f:
        image_bytes = f.read()

    print("preparing the prompt...")
    prompt = build_menu_extraction_prompt(filename)

    return receive_image_prompt(prompt,image_bytes)



async def save_dishes(payload: DishBulkIn, db: AsyncSession):
    created = []

    print("PAYLOAD:", payload)
    print("DISHES:", payload.dishes)

    for item in payload.dishes:
        print("ITEM:", item)

        price = item.price or 0.0

        new_dish = Dish(
            name=item.name,
            description=item.description,
            price=price,
            category=item.category,
            image_url=item.image_url,
            available=item.available,
            tags=item.tags,
            extraction_confidence=item.extraction_confidence,
            extraction_source=item.extraction_source,
        )
        db.add(new_dish)
        created.append(new_dish)

    await db.commit()

    for new_dish in created:
        await db.refresh(new_dish)

    print("CREATED IDS:", [new_dish.id for new_dish in created])

    return {
        "message": "Dishes saved successfully",
        "count": len(created),
        "ids": [new_dish.id for new_dish in created]
    }