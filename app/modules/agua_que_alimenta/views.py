from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Água que Alimenta Views"])
from jinja2 import Environment, FileSystemLoader  # noqa: E402
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

async def get_user_context(request: Request):
    is_admin = False
    user_username = "Anônimo"
    token = request.cookies.get("access_token")
    if token:
        try:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            from jose import jwt
            from app.core.auth.utils import SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_username = payload.get("sub", "Anônimo")
            
            from app.core.database import get_supabase
            supabase = get_supabase()
            res_user = supabase.table('users').select('role').eq('username', user_username).execute()
            if res_user.data and res_user.data[0].get('role') == 'admin':
                is_admin = True
        except Exception:
            pass
    return {"is_admin": is_admin, "user_username": user_username}

@router.get("/consolidado", response_class=HTMLResponse)
async def get_consolidado_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/consolidado.html", context={"current_page": "consolidado", **ctx})

@router.get("/conferencia", response_class=HTMLResponse)
async def get_conferencia_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/conferencia.html", context={"current_page": "conferencia", **ctx})

@router.get("/graficos", response_class=HTMLResponse)
async def get_graficos_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/graficos.html", context={"current_page": "graficos", **ctx})

@router.get("/monitoramento-grh", response_class=HTMLResponse)
async def get_monitoramento_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/monitoramento-grh.html", context={"current_page": "monitoramento", **ctx})

@router.get("/beneficiarios", response_class=HTMLResponse, summary="Página da Tabela Completa")
async def get_tabela_completa(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/beneficiarios.html", context={"current_page": "beneficiarios", **ctx})

@router.get("/mapa", response_class=HTMLResponse, summary="Página do Mapa")
async def get_mapa(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="mapa/index.html", context={"current_page": "mapa", **ctx})

@router.get("/processar", response_class=HTMLResponse, summary="Página de Processamento")
async def get_processar_pagina(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/processar.html", context={"current_page": "processar", **ctx})

@router.get("/fila-validacao", response_class=HTMLResponse)
async def get_fila_validacao_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/fila-validacao.html", context={"current_page": "fila_validacao", **ctx})

@router.get("/documentacao", response_class=HTMLResponse)
async def get_documentacao_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/documentacao.html", context={"current_page": "documentacao", **ctx})

@router.get("/cronograma", response_class=HTMLResponse)
async def get_cronograma_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/cronograma.html", context={"current_page": "cronograma", **ctx})

@router.get("/validacao", response_class=HTMLResponse)
async def get_validacao_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/validacao.html", context={"current_page": "validacao", **ctx})

@router.get("/planejamento", response_class=HTMLResponse)
async def get_planejamento_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/planejamento.html", context={"current_page": "planejamento", **ctx})

@router.get("/pedreiros", response_class=HTMLResponse)
async def get_pedreiros_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/pedreiros.html", context={"current_page": "pedreiros", **ctx})
