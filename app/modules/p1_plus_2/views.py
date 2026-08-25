from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from app.config import settings

router = APIRouter(prefix="/p1-2", tags=["P1+2 Views"])
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

async def get_user_context(request: Request):
    is_admin = False
    user_username = "Anônimo"
    token = request.cookies.get("access_token")
    if token:
        try:
            if token.startswith(f"{settings.AUTH_BEARER_PREFIX} ") or token.startswith("Bearer "):
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
    return {"is_admin": is_admin, "user_username": user_username, "context_project": "p1_2"}

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
@router.get("/portal", response_class=HTMLResponse, summary="Portal P1+2")
async def get_portal_p12(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="p1_plus_2/portal.html", context={"current_page": "p12_portal", **ctx})

@router.get("/consolidado", response_class=HTMLResponse, summary="Consolidado P1+2")
async def get_consolidado_p12(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="p1_plus_2/consolidado.html", context={"current_page": "p12_consolidado", **ctx})

@router.get("/graficos", response_class=HTMLResponse, summary="Gráficos P1+2")
async def get_graficos_p12(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="p1_plus_2/graficos.html", context={"current_page": "p12_graficos", **ctx})

@router.get("/beneficiarios", response_class=HTMLResponse, summary="Beneficiários P1+2")
async def get_beneficiarios_p12(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="p1_plus_2/beneficiarios.html", context={"current_page": "p12_beneficiarios", **ctx})

@router.get("/beneficiarios/perfil/{id}", response_class=HTMLResponse, summary="Perfil do Beneficiário P1+2")
async def get_perfil_beneficiario_p12(request: Request, id: int):
    ctx = await get_user_context(request)
    from app.core.database import get_supabase, fetch_all
    try:
        supabase = get_supabase()
        res = supabase.table('p12_beneficiarios').select('*').eq('id', id).execute()
        beneficiario = res.data[0] if res.data else None
    except Exception:
        all_ben = fetch_all('p12_beneficiarios')
        beneficiario = next((b for b in all_ben if b.get('id') == id), None)

    if not beneficiario:
        return templates.TemplateResponse(request=request, name="errors/404.html", context={"current_page": "404", **ctx}, status_code=404)

    return templates.TemplateResponse(request=request, name="p1_plus_2/perfil_beneficiario.html", context={"current_page": "p12_beneficiarios", "beneficiario": beneficiario, **ctx})

@router.get("/plano-produtivo", response_class=HTMLResponse, summary="Acompanhamento Plano Produtivo P1+2")
async def get_plano_produtivo_p12(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="p1_plus_2/plano_produtivo.html", context={"current_page": "p12_plano_produtivo", **ctx})

@router.get("/monitoramento", response_class=HTMLResponse, summary="Monitoramento Unificado P1+2")
async def get_monitoramento_p12(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="p1_plus_2/monitoramento.html", context={"current_page": "p12_monitoramento", **ctx})

@router.get("/cotacoes", response_class=HTMLResponse, summary="Cotações P1+2")
async def get_cotacoes_p12(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="p1_plus_2/cotacoes.html", context={"current_page": "p12_cotacoes", **ctx})

@router.get("/documentacao", response_class=HTMLResponse, summary="Documentação P1+2")
async def get_documentacao_p12(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="p1_plus_2/documentacao.html", context={"current_page": "p12_documentacao", **ctx})

@router.get("/planejamento", response_class=HTMLResponse, summary="Planejamento P1+2")
async def get_planejamento_p12(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="p1_plus_2/planejamento.html", context={"current_page": "p12_planejamento", **ctx})