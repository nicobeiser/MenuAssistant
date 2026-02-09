from google import genai
from google.genai import types
from dotenv import load_dotenv
from load_image import load_all_images
import os

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
        return "No menu images have been uploaded yet. Please upload at least one image."

    print(full_prompt)

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            *images,
            full_prompt,
        ],
    )

    texts = []
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            texts.append(part.text)

    final_text = "".join(texts)
    print(final_text)
    return final_text


if __name__ == "__main__":
    DEBUG = True
