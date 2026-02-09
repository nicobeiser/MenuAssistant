# MenuAssistant (testgemini)

A simple API that analyzes a restaurant menu image (JPG/JPEG) using Google Gemini and returns **3 menu-based recommendations** with:
- dish name
- price
- a short reason (≤ 50 characters)

The AI **must not** use any information that is not present in the menu image.

---

## Requirements

- Python 3.10 or higher
- Google Gemini API key
- pip

---

## Setup

### 1) Clone the repository

```bash
git clone git@github.com:nicobeiser/testgemini.git
cd testgemini
```

### 2) Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows PowerShell
```



### 3) Install dependencies
```bash
pip install -U pip
pip install fastapi uvicorn python-dotenv google-genai requests python-multipart
```

### 4) Environment variables
Create a .env file in the project root:
API_KEY=YOUR_GEMINI_API_KEY
⚠️ Do NOT commit this file.


### 5) Menu images
Menu images are uploaded at runtime via the web UI or the `POST /upload` endpoint.
They are stored in the `images/` folder. You can also place images there manually.
Supported formats: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`.


----------------------------------------------------------------------------------------


## Project Structure

```text
testgemini/
├── main.py              # FastAPI application (API endpoints)
├── first.py             # Gemini logic (receive_prompt)
├── load_image.py        # Image loading utilities
├── pdf_to_png.py        # PDF to PNG converter
├── images/              # Uploaded menu images (user-managed)
├── .env                 # Environment variables (not committed)
├── frontend/            # Simple web UI
│   ├── chat.html
│   ├── chat.js
│   └── styles.css
└── README.md
```



----------------------------------------------------------------------------------------


### Running the API

Start the development server:

```bash
uvicorn main:app --reload
```
The API will be available at:

## http://127.0.0.1:8000

Swagger UI: http://127.0.0.1:8000/docs


----------------------------------------------------------------------------------------


### API Usage

#### Upload menu images
```bash
curl -X POST http://127.0.0.1:8000/upload \
  -F "files=@Menu.png" \
  -F "files=@Menu.jpeg"
```

#### List uploaded images
```bash
curl http://127.0.0.1:8000/images
```

#### Delete a specific image
```bash
curl -X DELETE http://127.0.0.1:8000/images/Menu.png
```

#### Delete all images
```bash
curl -X DELETE http://127.0.0.1:8000/images
```

#### Chat (ask about the menu)
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What are 3 recommended dishes?"}'
```

Response:
```json
{
  "reply": "1) Dish - price - reason\n2) ...\n3) ..."
}
```

If no images have been uploaded, the API will ask you to upload at least one.
If the question cannot be answered using only the menu content,
the API will explicitly state that it cannot answer.


----------------------------------------------------------------------------------------


### Notes
The model is constrained to use only menu content.
If prices or dishes are not visible in the image, no assumptions are made.
Designed for experimentation and educational purposes.









