# MenuAssistant

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
pip install fastapi uvicorn python-dotenv google-genai requests
```

### 4) Environment variables
Create a .env file in the project root:
API_KEY=YOUR_GEMINI_API_KEY
⚠️ Do NOT commit this file.


### 5) This step was not intended to be on the main branch,
but we forgot to remove it. Unfortunately, we can’t modify the main README now,
as we would be disqualified from the hackathon.


----------------------------------------------------------------------------------------


## Project Structure

```text
testgemini/
├── main.py              # FastAPI application (API endpoints)
├── first.py             # Gemini logic (receive_prompt)
├── load_image.py        # Python script to load the image on the API
├── .env                 # Environment variables (not committed)
├── images/              # Images uploaded
├── frontend/            # Simple web UI
│   ├── chat.html
│   ├── admin.css
│   ├── admin.html
│   ├── admin.js
│   ├── chat.js
│   ├── styles.css
│   ├── favicon.ico
│   └── favicon.png
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

```bash
POST /chat
Send a question related to the uploaded menu images.

Request body:
{
  "message": "I want something vegetarian"
}

Example using curl:
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I want something vegetarian"}'
```

Response:
{
  "reply": "1) Dish - price - reason\n2) ...\n3) ..."
}

---

```bash
POST /upload
Upload one or more menu images (multipart/form-data).
Field name: files

Example using curl:
curl -X POST http://127.0.0.1:8000/upload \
  -F "files=@menu1.jpg" \
  -F "files=@menu2.png"
```

Response:
{
  "uploaded": ["menu1.jpg", "menu2.png"]
}

---

```bash
GET /images
List all uploaded menu images.

Example using curl:
curl http://127.0.0.1:8000/images
```

Response:
{
  "images": ["menu1.jpg", "menu2.png"]
}

---

```bash
GET /images/{filename}/file
Return the actual image binary for preview.
```

---

```bash
DELETE /images/{filename}
Delete a specific uploaded image.

Example using curl:
curl -X DELETE http://127.0.0.1:8000/images/menu1.jpg
```

Response:
{
  "deleted": "menu1.jpg"
}

---

```bash
DELETE /images
Delete all uploaded menu images.

Example using curl:
curl -X DELETE http://127.0.0.1:8000/images
```

Response:
{
  "status": "all images deleted"
}




----------------------------------------------------------------------------------------

## Gemini Prompt Logic

The core AI logic is implemented in the `recieve_prompt(prompt)` function.

### System Prompt Design

The system prompt strictly enforces the following rules:

- Analyze **only** the provided menu images
- Do **not** use external knowledge or assumptions
- Return **exactly 3 dishes**
- Each dish must include:
  - name
  - price
  - a short reason (**≤ 50 characters**)
- If the request:
  - cannot be answered using the menu image
  - or is unrelated to menu data or recommendations  
  the model must explicitly state that it cannot answer

The user message is appended to the system prompt to guide the recommendation request.

---

### Multimodal Input

The Gemini model receives:

- 📷 The menu images
- 📝 The composed text prompt (system instructions + user input)

This ensures that **all recommendations are image-driven**.

---

### Gemini Configuration

- **Model:** `gemini-3-flash-preview`
- **Input type:** Multimodal (image + text)
- **Enabled tool:**
  - `code_execution`  
    (enabled for compatibility and future extensibility, not required for reasoning)

---

### Output Processing

- The response text is extracted from Gemini’s structured output
- All text parts are concatenated into a single readable string
- The final response is returned directly by the API

---

### Design Goals

- Prevent hallucinations
- Enforce strict output format
- Ensure reproducible and explainable results
- Keep responses concise and menu-faithful


----------------------------------------------------------------------------------------


### Notes
The model is constrained to use only menu content.
If prices or dishes are not visible in the image, no assumptions are made.
Designed for experimentation and educational purposes.











