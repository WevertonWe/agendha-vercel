import os
import sys

# No Windows (Python 3.8+), registra diretórios de DLLs nativas caso o Python venha do QGIS ou ambiente sem DLLs globais
if sys.platform == "win32":
    for qgis_bin in [
        r"C:\Program Files\QGIS 3.44.12\bin",
        r"C:\Program Files\QGIS 3.44.12\apps\Python312\DLLs",
        r"C:\Program Files\QGIS 3.44.12\apps\Python312",
        r"C:\Program Files\QGIS 3.44.12\apps\qt5\bin",
        r"C:\Program Files\QGIS 3.34.0\bin",
        r"C:\Program Files\QGIS 3.34.0\apps\Python312\DLLs",
        r"C:\Program Files\QGIS 3.32.0\bin"
    ]:
        if os.path.exists(qgis_bin):
            try:
                os.add_dll_directory(qgis_bin)
            except Exception:
                pass


import logging
from contextlib import asynccontextmanager
from jinja2 import Environment, FileSystemLoader  # noqa: E402

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
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


_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=400)

def safely_split(value, delimiter='-'):
    if isinstance(value, dict):
        return []
    return str(value).split(delimiter)

_env.filters['safely_split'] = safely_split
templates = Jinja2Templates(env=_env)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Executa tarefas de inicialização e limpeza.
    """
    logging.info("Servidor a arrancar...")
    
    # Na Vercel, a criação de pastas em tempo de execução é proibida (Read-only FS).
    # A estrutura básica deve vir do repositório (.gitkeep) ou ser ignorada se opcional.
    logging.info("Pulando criação de pastas físicas (Ambiente Cloud).")

    # 2. Inicialização de Ficheiros (Desativado em Ambiente Cloud)
    # if not os.path.exists(settings.HISTORICO_PATH):
    #     with open(settings.HISTORICO_PATH, 'w', encoding='utf-8') as f:
    #         json.dump([], f, ensure_ascii=False, indent=4)

    # 3. Verificação de Motores PDF
    # verificar_motores_pdf()
    
    # 4. Inicialização do Banco de Dados (Core)
    from app.core.database import init_db, sync_projects
    try:
        init_db()
    except Exception as e:
        logging.error(f"⚠️ ERRO no init_db (servidor continua): {e}")

    # 4.2 Sincronização de projetos com Supabase (non-blocking)
    try:
        sync_projects()
    except Exception as e:
        logging.warning(f"⚠️ sync_projects falhou (non-fatal): {e}")

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

    logging.info(">>> FIM INICIALIZAÇÃO <<<")

    # 5. Inicialização do Scheduler de Tarefas (Backup & Auditoria BSF)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(realizar_backup_agora, 'cron', hour=23, minute=0)

    # Auditoria diária de conformidade e pastas às 08:30
    async def executar_auditoria_matinal_bsf():
        try:
            from app.modules.bahia_sem_fome.services.auditoria_service import executar_auditoria_completa_pastas_locais
            logging.info("Iniciando auditoria diária matinal das pastas do Bahia Sem Fome (08:30)...")
            executar_auditoria_completa_pastas_locais(auto_consolidar_acentos=False)
            logging.info("Auditoria matinal BSF concluída com sucesso.")
        except Exception as e:
            logging.error(f"Erro na auditoria matinal BSF: {e}")

    scheduler.add_job(executar_auditoria_matinal_bsf, 'cron', hour=8, minute=30)
    scheduler.start()
    logging.info("Scheduler de backup e auditoria BSF iniciado.")

    # Executa uma auditoria inicial em background no startup se local
    try:
        asyncio.create_task(executar_auditoria_matinal_bsf())
    except Exception:
        pass
    
    from app.services.queue_service import queue_manager
    queue_manager.start()
    
    yield
    logging.info("Servidor a desligar...")
    queue_manager.stop()


# --- Configuração da Aplicação FastAPI ---
app = FastAPI(
    title="Água que Alimenta API",
    description="API para processamento de documentos de beneficiários.",
    version="1.0.0",
    lifespan=lifespan
)

from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/api/force-create")
async def force_create():
    import os
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        return {"status": "Erro", "detalhe": "SUPABASE_URL ou SUPABASE_KEY ausentes"}

    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        
        res = supabase.table('users').insert({
            "username": "vitoria_teste",
            "password_hash": "hash_fake",
            "full_name": "Usuário Criado pelo Site",
            "is_active": True
        }).execute()
        return {"status": "Tentativa concluída", "resultado": res.data}
    except Exception as e:
        return {"status": "Erro na execução", "detalhe": str(e)}

# --- Middleware de Log de Acesso ---
# --- Middleware de Log de Navegação (AuditLogs) ---
# @app.middleware("http")
# async def log_navigation(request: Request, call_next):
#     return await call_next(request)

# --- Exception Handlers Globais ---
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logging.error(f"Erro 500 capturado: {exc}", exc_info=True)
    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor. Contate o suporte."}
        )
    return HTMLResponse(content="<h1>Erro Interno 500</h1>", status_code=500)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse(status_code=404, content={"detail": "Não encontrado"})
    return HTMLResponse(content="<h1>Erro 404 - Não encontrado</h1>", status_code=404)


# --- Montagem de Arquivos Estáticos ---
class CachedStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

app.mount("/static", CachedStaticFiles(directory=settings.STATIC_FOLDER), name="static")

# Verificação de existência da pasta para evitar o RuntimeError da Starlette
upload_path = settings.UPLOAD_FOLDER
if os.path.exists(upload_path):
    app.mount("/uploads", StaticFiles(directory=upload_path), name="uploads")
else:
    # Na Vercel, se a pasta não subir no deploy, o app não deve crashar
    logging.warning(f"Alerta de Boot: Diretório {upload_path} não encontrado. Ignorando mount de estáticos.")

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

# Admin Audit & Assets
from app.routers.admin_audit import router as admin_audit_router  # noqa: E402
from app.routers.admin_assets import router as admin_assets_router  # noqa: E402
app.include_router(admin_audit_router)
app.include_router(admin_assets_router)

# Ferramentas
from app.routers.ferramentas import router as ferramentas_router  # noqa: E402
app.include_router(ferramentas_router)

# Módulo: Projetos (Hub e Sugestões)
from app.modules.projetos.routers import router as projetos_router  # noqa: E402
app.include_router(projetos_router)

from app.modules.bahia_sem_fome.routers import renomeador as bsf_renomeador  # noqa: E402
from app.modules.bahia_sem_fome.routers import atestes as bsf_atestes  # noqa: E402
from app.modules.bahia_sem_fome.routers import beneficiarios as bsf_beneficiarios  # noqa: E402
from app.modules.bahia_sem_fome.routers import scanner as bsf_scanner  # noqa: E402
from app.modules.bahia_sem_fome import views as bsf_views  # noqa: E402
from app.modules.bahia_sem_fome.routers import classificador as bsf_classificador

from app.modules.bahia_sem_fome.routers import auditoria as bsf_auditoria  # noqa: E402

app.include_router(bsf_renomeador.router)
app.include_router(bsf_atestes.router)
app.include_router(bsf_beneficiarios.router)
app.include_router(bsf_scanner.router)
app.include_router(bsf_views.router)
app.include_router(bsf_classificador.router)
app.include_router(bsf_auditoria.router)

# Módulo: Projeto P1+2
from app.modules.p1_plus_2 import views as p12_views  # noqa: E402
from app.modules.p1_plus_2.routers import (  # noqa: E402
    beneficiarios as p12_beneficiarios,
    consolidado as p12_consolidado,
    monitoramentos as p12_monitoramentos,
    plano_produtivo as p12_plano_produtivo,
    cotacoes as p12_cotacoes,
    documentos as p12_documentos,
    planejamento as p12_planejamento
)
app.include_router(p12_views.router)
app.include_router(p12_beneficiarios.router)
app.include_router(p12_consolidado.router)
app.include_router(p12_monitoramentos.router)
app.include_router(p12_plano_produtivo.router)
app.include_router(p12_cotacoes.router)
app.include_router(p12_documentos.router)
app.include_router(p12_planejamento.router)



print("\n[MAPA DE ROTAS ATIVAS NO FASTAPI]")
for route in app.routes:
    if hasattr(route, "path"):
        methods = getattr(route, "methods", "N/A")
        print(f"  Rota: {route.path} | Metodos: {methods}")
print("================================================\n")

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

