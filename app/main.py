import os
import json
import logging
from contextlib import asynccontextmanager

import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.dependencies import manager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.modules.backup.services import realizar_backup_agora
from app.modules.backup.routes import router as backup_router

# --- Imports de Rotas (Routers) ---
# Core
from app.core import views as core_views
from app.core import auth

# Módulo: Água que Alimenta
from app.modules.agua_que_alimenta.routers import (
    beneficiarios,
    eventos,
    documentos,
    cronograma,
    ocr,
    pedreiros,
    grh,
    logistica
)
from app.modules.agua_que_alimenta import views as agua_views

# Módulo: Cotações
from app.modules.cotacoes.routers import cotacoes
from app.modules.cotacoes import views as cotacoes_views

# Módulo: Financeiro
from app.modules.financeiro.routes import router as financeiro_router
from app.modules.financeiro import views as financeiro_views

# Módulo: Dashboard
from app.modules.dashboard import views as dashboard_views

# Módulo: Ofícios
from app.modules.oficios.routes import router as oficios_router

# Módulo: Fornecedores
from app.modules.fornecedores.routers import fornecedores as fornecedores_router


# --- Configuração do Logging ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

templates = Jinja2Templates(directory=settings.TEMPLATES_FOLDER)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Executa tarefas de inicialização e limpeza.
    """
    logging.info("Servidor a arrancar...")
    
    # 1. Criação das Pastas Necessárias
    pastas_a_criar = [
        settings.STATIC_FOLDER,
        settings.TEMPLATES_FOLDER,
        settings.UPLOAD_FOLDER,
        settings.PRINT_FOLDER,
        settings.DOCUMENTOS_FOLDER,
        settings.COTACOES_FOLDER,
        settings.GRH_FOLDER,
        settings.BENEFICIARIOS_DOCS_FOLDER,
        settings.TEMP_FOLDER,
        settings.UPLOAD_FOLDER / "temp",
        settings.TEMPLATES_FOLDER / "excel"
    ]
    for pasta in pastas_a_criar:
        os.makedirs(pasta, exist_ok=True)

    # 2. Inicialização de Ficheiros
    if not os.path.exists(settings.HISTORICO_PATH):
        with open(settings.HISTORICO_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    # 3. Verificação de Motores PDF
    # verificar_motores_pdf()
    
    # 4. Inicialização do Banco de Dados (Core)
    from app.core.database import init_db
    try:
        init_db()
    except Exception as e:
        logging.error(f"⚠️ ERRO no init_db (servidor continua): {e}")

    # 4.1 Validação de Ferramentas Externas
    import shutil
    tools_to_check = [
        ("Office Suite (Libre/Excel)", settings.LIBREOFFICE_PATH),
        ("Poppler", settings.POPPLER_PATH),
        ("Tesseract", settings.TESSERACT_CMD)
    ]
    logging.info("--- Verificando Ferramentas Externas ---")
    for name, path in tools_to_check:
        if not path:
            logging.warning(f"⚠️  {name}: NÃO CONFIGURADO (Defina no .env).")
            continue
            
        # Poppler é geralmente configurado como um diretório contendo os binários
        if name == "Poppler":
            if os.path.isdir(path):
                 logging.info(f"✅ {name}: OK (Diretório encontrado)")
            else:
                 logging.warning(f"⚠️  {name}: Diretório NÃO ENCONTRADO: {path}")
            continue

        # Para executáveis (LibreOffice, Tesseract)
        if shutil.which(path):
            logging.info(f"✅ {name}: OK")
        else:
            logging.warning(f"⚠️  {name}: Executável NÃO ENCONTRADO no caminho: {path}")
    logging.info("----------------------------------------")

    # --- DEBUG ROTAS (Solicitado: REMOVIDO PARA LIMPEZA) ---
    # for route in app.routes:
    #     if hasattr(route, "path"):
    #          logging.info(f"Rota Ativa: {route.path}")
    logging.info(">>> FIM LISTA ROTAS <<<")
    # --------------------------------

    # 5. Inicialização do Scheduler de Backup
    scheduler = AsyncIOScheduler()
    scheduler.add_job(realizar_backup_agora, 'cron', hour=23, minute=0)
    scheduler.start()
    logging.info("Scheduler de backup iniciado.")
    
    yield
    logging.info("Servidor a desligar...")


# --- Configuração da Aplicação FastAPI ---
app = FastAPI(
    title="Água que Alimenta API",
    description="API para processamento de documentos de beneficiários.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Middleware de Log de Acesso ---
# --- Middleware de Log de Navegação (AuditLogs) ---
@app.middleware("http")
async def log_navigation(request: Request, call_next):
    # 1. Processa a requisição
    response = await call_next(request)
    
    # 2. Filtros: Ignorar estáticos, API (exceto se importante), e favicon
    path = request.url.path
    if (path.startswith("/static") or 
        path.startswith("/favicon.ico") or 
        request.method == "OPTIONS"):
        return response

    # 3. Extração do Usuário
    username = "Anônimo"
    try:
        # Tenta pegar do state (se auth middleware rodou antes)
        if hasattr(request.state, "user"):
             user = request.state.user
             username = user.get("username", "Anônimo") if isinstance(user, dict) else getattr(user, "username", "Anônimo")
        else:
            # Fallback: Decodificar Token Manualmente
            token = request.cookies.get("access_token")
            if token:
                if token.startswith("Bearer "):
                    token = token.split(" ")[1]
                
                from app.core.auth.utils import SECRET_KEY, ALGORITHM
                from jose import jwt
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub", "Anônimo")
    except Exception:
        pass # Mantém Anônimo em falha de decode

    # 4. Registrar apenas GETs de Páginas (Navegação) ou Ações de Escrita não capturadas pelo Wrapper?
    # O Wrapper pega INSERT/UPDATE/DELETE. Aqui focamos em ACESSO (Leitura/Navegação).
    if request.method == "GET" and not path.startswith("/api"):
        try:
            # Usa conexão dedicada para não interferir na thread principal
            conn = sqlite3.connect(settings.DB_PATH)
            cursor = conn.cursor()
            
            from app.core.time_utils import get_bahia_time_str
            # Detalhes do Acesso
            detalhes = f"Acessou: {path}"
            
            cursor.execute("""
                INSERT INTO audit_logs (usuario_id, tabela, operacao, detalhes, valor_antigo, valor_novo, data_hora)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, "N/A", "ACESSO", detalhes, None, None, get_bahia_time_str()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Erro ao registrar Audit de Navegação: {e}")
            
    return response

# --- Exception Handlers Globais ---
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logging.error(f"Erro 500 capturado: {exc}", exc_info=True)
    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor. Contate o suporte."}
        )
    return templates.TemplateResponse("errors/500.html", {"request": request}, status_code=500)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse(status_code=404, content={"detail": "Não encontrado"})
    return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=404)


# --- Montagem de Arquivos Estáticos ---
app.mount("/static", StaticFiles(directory=settings.STATIC_FOLDER), name="static")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")

# --- Inclusão de Rotas (Routers) ---
# Core
app.include_router(core_views.router)
app.include_router(auth.router)
app.include_router(backup_router)

# Água que Alimenta
app.include_router(agua_views.router)
app.include_router(beneficiarios.router)
app.include_router(beneficiarios.router_root) # Router auxiliar para /api/salvar-validado sem prefixo extra
app.include_router(eventos.router)
app.include_router(documentos.router)
app.include_router(cronograma.router)
app.include_router(ocr.router)
app.include_router(pedreiros.router)
app.include_router(grh.router)
app.include_router(logistica.router)

# Cotações
app.include_router(cotacoes_views.router)
app.include_router(cotacoes.router)

# Financeiro
app.include_router(financeiro_views.router)
app.include_router(financeiro_router)

# Dashboard
app.include_router(dashboard_views.router)
app.include_router(dashboard_views.router)
# app.include_router(dashboard.router) # Antigo
from app.modules.dashboard.routers import api as dashboard_api  # noqa: E402
app.include_router(dashboard_api.router)

# Ofícios
app.include_router(oficios_router)

# Fornecedores
from app.modules.fornecedores import views as fornecedores_views  # noqa: E402
app.include_router(fornecedores_router.router)
app.include_router(fornecedores_views.router)

# Materiais
from app.modules.materiais.routers import materiais as materiais_router  # noqa: E402
from app.modules.materiais import views as materiais_views  # noqa: E402
app.include_router(materiais_router.router)
app.include_router(materiais_views.router)

# Planejamento
from app.modules.planejamento.routers import planejamento as planejamento_router  # noqa: E402
app.include_router(planejamento_router.router)

# Mapa Interativo
from app.modules.mapa.routes import router as mapa_router, view_router as mapa_view_router  # noqa: E402
app.include_router(mapa_router)
app.include_router(mapa_view_router)

# Admin Audit
from app.routers.admin_audit import router as admin_audit_router  # noqa: E402
app.include_router(admin_audit_router)

# Módulo: Projetos (Hub e Sugestões)
from app.modules.projetos.routers import router as projetos_router  # noqa: E402
app.include_router(projetos_router)

# Módulo: Bahia Sem Fome (BSF)
from app.modules.bahia_sem_fome.routers import metas as bsf_metas  # noqa: E402
from app.modules.bahia_sem_fome.routers import visitas as bsf_visitas  # noqa: E402
from app.modules.bahia_sem_fome.routers import renomeador as bsf_renomeador  # noqa: E402
from app.modules.bahia_sem_fome.routers import atestes as bsf_atestes  # noqa: E402
from app.modules.bahia_sem_fome import views as bsf_views  # noqa: E402

print("DEBUG: Incluindo rotas do BSF no FastAPI...")
app.include_router(bsf_metas.router)
app.include_router(bsf_visitas.router)
app.include_router(bsf_renomeador.router)
app.include_router(bsf_atestes.router)
app.include_router(bsf_views.router)


# --- Endpoint WebSocket ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Gerencia a conexão WebSocket para comunicação em tempo real."""
    await manager.connect(websocket)
    try:
        while True:
            # Mantém a conexão viva, ignorando mensagens do cliente
            await websocket.receive_text()
    except WebSocketDisconnect:
        logging.info("Cliente %s desconectado.", websocket.client)
    except RuntimeError as e_runtime:
        logging.error(
            "Erro de Runtime na conexão WebSocket com %s: %s",
            websocket.client, e_runtime, exc_info=True
        )
    except Exception as e_ws:  # pylint: disable=broad-except
        logging.error(
            "Erro inesperado na conexão WebSocket com %s: %s",
            websocket.client, e_ws, exc_info=True
        )
    finally:
        manager.disconnect(websocket)

