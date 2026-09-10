
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/projetos/ater-bahia-sem-fome", tags=["BSF Views"])
from jinja2 import Environment, FileSystemLoader  # noqa: E402
from app.core.auth.utils import get_user_context_from_request

_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=400)
templates = Jinja2Templates(env=_env)

async def get_user_context(request: Request):
    return get_user_context_from_request(request, default_context_project="bsf")


@router.get("/producao", response_class=HTMLResponse)
async def get_producao_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="bahia-sem-fome/producao.html", context={"current_page": "bsf_producao", **ctx})

@router.get("/renomeador", response_class=HTMLResponse)
async def get_renomeador_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="bahia-sem-fome/renomeador.html", context={"current_page": "bsf_renomeador", **ctx})


@router.get("/atestes", response_class=HTMLResponse)
async def get_atestes_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="bahia-sem-fome/gerador_atestes.html", context={"current_page": "bsf_atestes", **ctx})


@router.get("/beneficiarios", response_class=HTMLResponse)
async def get_beneficiarios_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="bahia-sem-fome/beneficiarios.html", context={"current_page": "bsf_beneficiarios", **ctx})
