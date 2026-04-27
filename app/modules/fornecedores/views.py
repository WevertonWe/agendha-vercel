from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter(tags=["Fornecedores Views"])
templates = Jinja2Templates(directory=settings.TEMPLATES_FOLDER)

@router.get("/fornecedores", response_class=HTMLResponse)
async def get_fornecedores_page(request: Request):
    return templates.TemplateResponse("fornecedores/index.html", {"request": request, "current_page": "fornecedores"})
