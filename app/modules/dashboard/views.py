from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter(tags=["Dashboard Views"])
templates = Jinja2Templates(directory=settings.TEMPLATES_FOLDER)

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_page(request: Request):
    # TODO: Criar template dashboard.html
    return templates.TemplateResponse("agua/portal.html", {"request": request, "current_page": "dashboard", "message": "Módulo Dashboard em Construção"})
