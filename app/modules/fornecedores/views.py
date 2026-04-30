from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Fornecedores Views"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

@router.get("/fornecedores", response_class=HTMLResponse)
async def get_fornecedores_page(request: Request):
    return templates.TemplateResponse("fornecedores/index.html", {"request": request, "current_page": "fornecedores"})
