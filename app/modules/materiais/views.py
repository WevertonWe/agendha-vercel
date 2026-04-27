from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter(tags=["Materiais Views"])
templates = Jinja2Templates(directory=settings.TEMPLATES_FOLDER)

@router.get("/materiais", response_class=HTMLResponse)
async def get_materiais_page(request: Request):
    return templates.TemplateResponse("materiais/index.html", {"request": request, "current_page": "materiais"})
