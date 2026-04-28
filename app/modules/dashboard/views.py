from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter(tags=["Dashboard Views"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_page(request: Request):
    # TODO: Criar template dashboard.html
    return templates.TemplateResponse("agua/portal.html", {"request": request, "current_page": "dashboard", "message": "Módulo Dashboard em Construção"})
