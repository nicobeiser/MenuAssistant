from google import genai
from google.genai import types
from dotenv import load_dotenv
from load_image import load_all_images
from typing import Any, Dict, Tuple
import os
import time


load_dotenv()

API_KEY = os.getenv("API_KEY")

client = genai.Client(api_key=API_KEY)


def recieve_prompt(prompt):
    system_prompt = (
        "Analyze the menu and answer the following question."
        " Do not use any information that is not present in the menu."
        " Provide 3 dishes in a simple way, each with its price and a short reason for the choice"
        " (the reason must be no longer than 50 characters)."
        " If you cannot answer because there is not enough information,"
        " or the message is not a request for menu data or a recommendation,"
        " simply state that you cannot answer."
    )

    full_prompt = system_prompt + prompt

    images = load_all_images()

    if not images:
        return {
            "text": "No menu images have been uploaded yet. Please upload at least one image.",
            "metrics": {
                "model_latency_ms": 0,
                "images_count": 0,
                "prompt_chars": len(full_prompt),
                "ok": False,
                "error": "no_images",
                "usage": None,
            },
        }

    print(full_prompt)

    t0 = time.perf_counter()
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                *images,
                full_prompt,
            ],
        )
        latency_ms = (time.perf_counter() - t0) * 1000
    except Exception as e:
        latency_ms = (time.perf_counter() - t0) * 1000
        return {
            "text": "Model error. Try again.",
            "metrics": {
                "model_latency_ms": latency_ms,
                "images_count": len(images),
                "prompt_chars": len(full_prompt),
                "ok": False,
                "error": type(e).__name__,
            },
        }
        

    texts = []
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            texts.append(part.text)

    final_text = "".join(texts)
    print(final_text)


    usage = getattr(response, "usage_metadata", None) or getattr(response, "usage", None)

    return {
        "text": final_text,
        "metrics": {
            "model_latency_ms": latency_ms,
            "images_count": len(images),
            "prompt_chars": len(full_prompt),
            "ok": True,
            "usage": str(usage) if usage is not None else None,
        },
    }


if __name__ == "__main__":
    DEBUG = True
