from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import json
import logging
from app.config import settings

router = APIRouter(tags=["Core Views"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

@router.get("/", response_class=HTMLResponse, summary="Página Portal")
async def get_portal_page(request: Request):
    # Redireciona para o login por padrão, como solicitado
    return RedirectResponse(url="/login")


@router.get("/portal", response_class=HTMLResponse)
async def get_real_portal_page(request: Request):
    is_admin = False
    user_username = "Anônimo"
    token = request.cookies.get("access_token")
    if token:
        try:
            if token.startswith(f"{settings.AUTH_BEARER_PREFIX} "):
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
            
    return templates.TemplateResponse(request=request, name=str("agua/portal.html"), context={
        "request": request, 
        "current_page": "portal", 
        "is_admin": is_admin,
        "user_username": user_username,
        "context_project": "agua"
    })

@router.get("/hub", response_class=HTMLResponse)
async def get_admin_hub_page(request: Request):
    is_admin = False
    user_username = "Anônimo"
    user_role = "user"
    token = request.cookies.get("access_token")
    if token:
        try:
            if token.startswith(f"{settings.AUTH_BEARER_PREFIX} "):
                token = token.split(" ")[1]
            from jose import jwt
            from app.core.auth.utils import SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_username = payload.get("sub", "Anônimo")
            
            from app.core.database import get_supabase
            supabase = get_supabase()
            res_user = supabase.table('users').select('role').eq('username', user_username).execute()
            if res_user.data:
                user_role = res_user.data[0].get('role', 'user')
                if user_role == 'admin':
                    is_admin = True
        except Exception:
            pass
            
    if not is_admin:
         return RedirectResponse(url="/login")

    return templates.TemplateResponse(request=request, name=str("admin/admin_hub.html"), context={
        "request": request, 
        "current_page": "hub",
        "user_role": user_role,
        "user_username": user_username
    })

@router.get("/login")
async def get_login_page(request: Request):
    # Retornamos apenas o essencial para evitar o erro de hash no cache
    return templates.TemplateResponse(request=request, name=str("auth/login.html"), context={"request": request})

@router.get("/admin/users", response_class=HTMLResponse)
async def get_admin_users_page(request: Request):
    return templates.TemplateResponse(request=request, name=str("admin/usuarios.html"), context={"request": request})

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    if os.path.exists(settings.FAVICON_PATH):
        return FileResponse(
            settings.FAVICON_PATH, media_type="image/vnd.microsoft.icon"
        )
    raise HTTPException(status_code=404, detail="Favicon not found")

@router.get("/historico", summary="Obter Histórico de Processamentos")
async def get_historico_endpoint():
    try:
        with open(settings.HISTORICO_PATH, 'r', encoding='utf-8') as hist_file:
            historico_data = json.load(hist_file)
        return JSONResponse(content=historico_data)
    except FileNotFoundError:
        logging.warning(
            "Arquivo histórico %s não encontrado.", settings.HISTORICO_PATH
        )
        return JSONResponse(content=[], status_code=200)
    except json.JSONDecodeError:
        logging.error(
            "Erro ao decodificar JSON do histórico %s.", settings.HISTORICO_PATH
        )
        return JSONResponse(
            content={"error": "Erro ao ler o histórico."}, status_code=500
        )
    except IOError as e_io:
        logging.exception("Erro de I/O ao buscar histórico: %s", e_io)
        return JSONResponse(
            content={"error": "Erro interno ao buscar histórico."},
            status_code=500
        )
