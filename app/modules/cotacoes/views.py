from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from app.config import settings
from app.dependencies import get_db_connection

router = APIRouter(tags=["Cotações Views"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

@router.get("/cotacoes", response_class=HTMLResponse)
async def get_cotacoes_page(request: Request):
    return templates.TemplateResponse("agua/cotacoes.html", {"request": request, "current_page": "cotacoes"})

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

    return templates.TemplateResponse("agua/analise-revisao.html", {
        "request": request,
        "current_page": "cotacoes",
        "cotacao": dict(cotacao),
        "proposta1": p1,
        "proposta2": p2,
        "proposta3": p3,
        "texto_dinamico": texto_dinamico
    })
