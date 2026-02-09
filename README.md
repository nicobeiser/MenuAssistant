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
pip install fastapi uvicorn python-dotenv google-genai requests
```

### 4) Environment variables
Create a .env file in the project root:
API_KEY=YOUR_GEMINI_API_KEY
⚠️ Do NOT commit this file.


### 5) Menu image
Place the menu image in the project root and name it:
Menu.jpeg
The API will only use the information present in this image.


----------------------------------------------------------------------------------------


## Project Structure


testgemini/
├── main.py        # FastAPI application
├── first.py       # Gemini logic (recieve_prompt)
├── Menu.jpeg      # Menu image
├── .env           # Environment variables (not committed)
└── README.md



----------------------------------------------------------------------------------------


### Running the API
Start the development server:
uvicorn main:app --reload
The API will be available at:
http://127.0.0.1:8000
Swagger UI: http://127.0.0.1:8000/docs


----------------------------------------------------------------------------------------


### API Usage
POST /chat
Send a question related to the menu.
Request body:
{
  "message": "What are 3 recommended dishes?"
}
Example using curl:
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What are 3 recommended dishes?"}'
Response:
{
  "reply": "1) Dish - price - reason\n2) ...\n3) ..."
}
If the question cannot be answered using only the menu image,
the API will explicitly state that it cannot answer.


----------------------------------------------------------------------------------------


### Notes
The model is constrained to use only menu content.
If prices or dishes are not visible in the image, no assumptions are made.
Designed for experimentation and educational purposes.




