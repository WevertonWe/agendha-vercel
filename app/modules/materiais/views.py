from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter(tags=["Materiais Views"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

@router.get("/materiais", response_class=HTMLResponse)
async def get_materiais_page(request: Request):
    return templates.TemplateResponse("materiais/index.html", {"request": request, "current_page": "materiais"})
