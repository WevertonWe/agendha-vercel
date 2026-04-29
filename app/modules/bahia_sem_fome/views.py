
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter(prefix="/projetos/ater-bahia-sem-fome", tags=["BSF Views"])
from jinja2 import Environment, FileSystemLoader
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

