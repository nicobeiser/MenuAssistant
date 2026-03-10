from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = BASE_DIR / "tests" / "testParser"

@router.get("/test/parser")
def serve_test_parser():
    return FileResponse(TEST_DIR / "testParser.html")