from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter(tags=["Água que Alimenta Views"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

@router.get("/consolidado", response_class=HTMLResponse)
async def get_consolidado_page(request: Request):
    return templates.TemplateResponse("agua/consolidado.html", {"request": request, "current_page": "consolidado"})

@router.get("/conferencia", response_class=HTMLResponse)
async def get_conferencia_page(request: Request):
    return templates.TemplateResponse("agua/conferencia.html", {"request": request, "current_page": "conferencia"})

@router.get("/graficos", response_class=HTMLResponse)
async def get_graficos_page(request: Request):
    return templates.TemplateResponse("agua/graficos.html", {"request": request, "current_page": "graficos"})

@router.get("/monitoramento-grh", response_class=HTMLResponse)
async def get_monitoramento_page(request: Request):
    return templates.TemplateResponse("agua/monitoramento-grh.html", {"request": request, "current_page": "monitoramento"})

@router.get("/beneficiarios", response_class=HTMLResponse, summary="Página da Tabela Completa")
async def get_tabela_completa(request: Request):
    return templates.TemplateResponse("agua/beneficiarios.html", {"request": request, "current_page": "beneficiarios"})

@router.get("/mapa", response_class=HTMLResponse, summary="Página do Mapa")
async def get_mapa(request: Request):
    return templates.TemplateResponse("mapa/index.html", {"request": request, "current_page": "mapa"})

@router.get("/processar", response_class=HTMLResponse, summary="Página de Processamento")
async def get_processar_pagina(request: Request):
    return templates.TemplateResponse("agua/processar.html", {"request": request, "current_page": "processar"})

@router.get("/fila-validacao", response_class=HTMLResponse)
async def get_fila_validacao_page(request: Request):
    return templates.TemplateResponse("agua/fila-validacao.html", {"request": request, "current_page": "fila_validacao"})

@router.get("/documentacao", response_class=HTMLResponse)
async def get_documentacao_page(request: Request):
    return templates.TemplateResponse("agua/documentacao.html", {"request": request, "current_page": "documentacao"})

@router.get("/cronograma", response_class=HTMLResponse)
async def get_cronograma_page(request: Request):
    return templates.TemplateResponse("agua/cronograma.html", {"request": request, "current_page": "cronograma"})

@router.get("/validacao", response_class=HTMLResponse)
async def get_validacao_page(request: Request):
    return templates.TemplateResponse("agua/validacao.html", {"request": request, "current_page": "validacao"})

@router.get("/planejamento", response_class=HTMLResponse)
async def get_planejamento_page(request: Request):
    return templates.TemplateResponse("agua/planejamento.html", {"request": request, "current_page": "planejamento"})

@router.get("/pedreiros", response_class=HTMLResponse)
async def get_pedreiros_page(request: Request):
    return templates.TemplateResponse("agua/pedreiros.html", {"request": request, "current_page": "pedreiros"})
