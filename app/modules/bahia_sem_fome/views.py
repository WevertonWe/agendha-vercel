
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter(prefix="/projetos/ater-bahia-sem-fome", tags=["BSF Views"])
templates = Jinja2Templates(directory=settings.TEMPLATES_FOLDER)

@router.get("/producao", response_class=HTMLResponse)
async def get_producao_page(request: Request):
    return templates.TemplateResponse("bahia-sem-fome/producao.html", {"request": request, "current_page": "bsf_producao"})

@router.get("/visitas", response_class=HTMLResponse)
async def get_visitas_page(request: Request):
    return templates.TemplateResponse("bahia-sem-fome/visitas.html", {"request": request, "current_page": "bsf_visitas"})

@router.get("/renomeador", response_class=HTMLResponse)
async def get_renomeador_page(request: Request):
    return templates.TemplateResponse("bahia-sem-fome/renomeador.html", {"request": request, "current_page": "bsf_renomeador"})

@router.get("/atestes", response_class=HTMLResponse)
async def get_atestes_page(request: Request):
    return templates.TemplateResponse("bahia-sem-fome/gerador_atestes.html", {"request": request, "current_page": "bsf_atestes"})
