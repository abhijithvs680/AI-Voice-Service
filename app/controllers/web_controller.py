"""Web view controller - serves HTML."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["web"])

INDEX_HTML_PATH = Path(__file__).resolve().parent.parent / "views" / "index.html"


@router.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Serve the main UI."""
    content = INDEX_HTML_PATH.read_text(encoding="utf-8")
    return HTMLResponse(content=content)
