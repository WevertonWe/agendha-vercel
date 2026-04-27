import os
import json
import logging
import sqlite3
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.dependencies import get_db_connection

router = APIRouter(tags=["Views (HTML)"])
templates = Jinja2Templates(directory=settings.TEMPLATES_FOLDER)

from fastapi.responses import RedirectResponse  # noqa: E402

@router.get("/", response_class=HTMLResponse, summary="Página Portal")
async def get_portal_page(request: Request):
    # Redireciona para o login por padrão, como solicitado
    return RedirectResponse(url="/login")

@router.get("/portal", response_class=HTMLResponse)
async def get_real_portal_page(request: Request):
    return templates.TemplateResponse("portal.html", {"request": request, "current_page": "portal"})

@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/admin/users", response_class=HTMLResponse)
async def get_admin_users_page(request: Request):
    return templates.TemplateResponse("admin/usuarios.html", {"request": request})

@router.get("/consolidado", response_class=HTMLResponse)
async def get_consolidado_page(request: Request):
    return templates.TemplateResponse("consolidado.html", {"request": request, "current_page": "consolidado"})

@router.get("/conferencia", response_class=HTMLResponse)
async def get_conferencia_page(request: Request):
    return templates.TemplateResponse("conferencia.html", {"request": request, "current_page": "conferencia"})

@router.get("/graficos", response_class=HTMLResponse)
async def get_graficos_page(request: Request):
    return templates.TemplateResponse("graficos.html", {"request": request, "current_page": "graficos"})

@router.get("/monitoramento-grh", response_class=HTMLResponse)
async def get_monitoramento_page(request: Request):
    return templates.TemplateResponse("monitoramento-grh.html", {"request": request, "current_page": "monitoramento"})

@router.get("/beneficiarios", response_class=HTMLResponse, summary="Página da Tabela Completa")
async def get_tabela_completa(request: Request):
    return templates.TemplateResponse("beneficiarios.html", {"request": request, "current_page": "beneficiarios"})

@router.get("/mapa", response_class=HTMLResponse, summary="Página do Mapa")
async def get_mapa(request: Request):
    return templates.TemplateResponse("mapa.html", {"request": request, "current_page": "mapa"})

@router.get("/cotacoes", response_class=HTMLResponse)
async def get_cotacoes_page(request: Request):
    return templates.TemplateResponse("cotacoes.html", {"request": request, "current_page": "cotacoes"})

@router.get("/fornecedores", response_class=HTMLResponse)
async def get_fornecedores_page(request: Request):
    return templates.TemplateResponse("fornecedores/index.html", {"request": request, "current_page": "fornecedores"})

@router.get("/processar", response_class=HTMLResponse, summary="Página de Processamento")
async def get_processar_pagina(request: Request):
    return templates.TemplateResponse("processar.html", {"request": request, "current_page": "processar"})

@router.get("/fila-validacao", response_class=HTMLResponse)
async def get_fila_validacao_page(request: Request):
    return templates.TemplateResponse("fila-validacao.html", {"request": request, "current_page": "fila_validacao"})

@router.get("/documentacao", response_class=HTMLResponse)
async def get_documentacao_page(request: Request):
    return templates.TemplateResponse("documentacao.html", {"request": request, "current_page": "documentacao"})

@router.get("/cronograma", response_class=HTMLResponse)
async def get_cronograma_page(request: Request):
    return templates.TemplateResponse("cronograma.html", {"request": request, "current_page": "cronograma"})

@router.get("/validacao", response_class=HTMLResponse)
async def get_validacao_page(request: Request):
    return templates.TemplateResponse("validacao.html", {"request": request, "current_page": "validacao"})

@router.get("/planejamento", response_class=HTMLResponse)
async def get_planejamento_page(request: Request):
    return templates.TemplateResponse("planejamento.html", {"request": request, "current_page": "planejamento"})

@router.get("/pedreiros", response_class=HTMLResponse)
async def get_pedreiros_page(request: Request):
    return templates.TemplateResponse("pedreiros.html", {"request": request, "current_page": "pedreiros"})

@router.get("/cotacoes/analise/{cotacao_id}", response_class=HTMLResponse)
def get_pagina_revisao_analise(
    cotacao_id: int,
    request: Request,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cotacoes_master WHERE id = ?", (cotacao_id,))
    cotacao = cursor.fetchone()
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")

    cursor.execute(
        "SELECT * FROM propostas WHERE cotacao_master_id = ? ORDER BY valor ASC",
        (cotacao_id,)
    )
    propostas = cursor.fetchall()

    propostas_top3 = [None, None, None]
    for i, prop in enumerate(propostas[:3]):
        propostas_top3[i] = dict(prop)

    p1, p2, p3 = propostas_top3

    texto_dinamico = f"A Cotação Prévia de Preços nº {cotacao['codigo_cotacao']}, para {cotacao['descricao']}, "

    if not p1:
        texto_dinamico += "ainda não recebeu propostas."
    else:
        texto_dinamico += (
            f"teve como vencedora a empresa {p1['nome_fornecedor'].upper()}, "
            f"com o valor de R$ {p1['valor']:.2f}. "
        )
        if p2:
            texto_dinamico += (
                f"O proponente 2, {p2['nome_fornecedor'].upper()}, "
                f"apresentou o valor de R$ {p2['valor']:.2f}. "
            )
        if p3:
            texto_dinamico += (
                f"O proponente 3, {p3['nome_fornecedor'].upper()}, "
                f"apresentou o valor de R$ {p3['valor']:.2f}."
            )

    texto_dinamico += "\n\n(Texto gerado automaticamente. Revise antes de confirmar.)"

    return templates.TemplateResponse("analise-revisao.html", {
        "request": request,
        "current_page": "cotacoes",
        "cotacao": dict(cotacao),
        "proposta1": p1,
        "proposta2": p2,
        "proposta3": p3,
        "texto_dinamico": texto_dinamico
    })

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
