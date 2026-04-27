from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import json
import logging
from app.config import settings

router = APIRouter(tags=["Core Views"])
templates = Jinja2Templates(directory=settings.TEMPLATES_FOLDER)

@router.get("/", response_class=HTMLResponse, summary="Página Portal")
async def get_portal_page(request: Request):
    # Redireciona para o login por padrão, como solicitado
    return RedirectResponse(url="/login")


@router.get("/portal", response_class=HTMLResponse)
async def get_real_portal_page(request: Request):
    # Tenta obter o usuário do cookie (lógica simplificada para não quebrar se falhar)
    is_admin = False
    username = ""
    token = request.cookies.get("access_token")
    if token:
        try:
            # Remover 'Bearer ' se existir
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            
            from app.core.auth.utils import SECRET_KEY, ALGORITHM
            from jose import jwt
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role")
            username = payload.get("sub", "")
            if role in ['admin', 'diretoria']:
                is_admin = True
        except Exception as e:
            logging.error(f"Erro ao validar token no portal: {e}")

    return templates.TemplateResponse("agua/portal.html", {
        "request": request, 
        "current_page": "portal", 
        "is_admin": is_admin,
        "user_username": username,
        "context_project": "agua"
    })

@router.get("/hub", response_class=HTMLResponse)
async def get_admin_hub_page(request: Request):
    # Decodificar token para obter role e username
    role = "user"
    username = ""
    token = request.cookies.get("access_token")
    if token:
        try:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            from app.core.auth.utils import SECRET_KEY, ALGORITHM
            from jose import jwt
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role", "user")
            username = payload.get("sub", "")
        except:  # noqa: E722
            pass
            
    return templates.TemplateResponse("admin/admin_hub.html", {
        "request": request, 
        "current_page": "hub",
        "user_role": role,
        "user_username": username
    })

@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/admin/users", response_class=HTMLResponse)
async def get_admin_users_page(request: Request):
    return templates.TemplateResponse("admin/usuarios.html", {"request": request})

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
