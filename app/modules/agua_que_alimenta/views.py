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
    return templates.TemplateResponse(request=request, name="agua/consolidado.html", context={"current_page": "consolidado"})

@router.get("/conferencia", response_class=HTMLResponse)
async def get_conferencia_page(request: Request):
    return templates.TemplateResponse(request=request, name="agua/conferencia.html", context={"current_page": "conferencia"})

@router.get("/graficos", response_class=HTMLResponse)
async def get_graficos_page(request: Request):
    return templates.TemplateResponse(request=request, name="agua/graficos.html", context={"current_page": "graficos"})

@router.get("/monitoramento-grh", response_class=HTMLResponse)
async def get_monitoramento_page(request: Request):
    return templates.TemplateResponse(request=request, name="agua/monitoramento-grh.html", context={"current_page": "monitoramento"})

@router.get("/beneficiarios", response_class=HTMLResponse, summary="Página da Tabela Completa")
async def get_tabela_completa(request: Request):
    return templates.TemplateResponse(request=request, name="agua/beneficiarios.html", context={"current_page": "beneficiarios"})

@router.get("/mapa", response_class=HTMLResponse, summary="Página do Mapa")
async def get_mapa(request: Request):
    return templates.TemplateResponse(request=request, name="mapa/index.html", context={"current_page": "mapa"})

@router.get("/processar", response_class=HTMLResponse, summary="Página de Processamento")
async def get_processar_pagina(request: Request):
    return templates.TemplateResponse(request=request, name="agua/processar.html", context={"current_page": "processar"})

@router.get("/fila-validacao", response_class=HTMLResponse)
async def get_fila_validacao_page(request: Request):
    return templates.TemplateResponse(request=request, name="agua/fila-validacao.html", context={"current_page": "fila_validacao"})

@router.get("/documentacao", response_class=HTMLResponse)
async def get_documentacao_page(request: Request):
    return templates.TemplateResponse(request=request, name="agua/documentacao.html", context={"current_page": "documentacao"})

@router.get("/cronograma", response_class=HTMLResponse)
async def get_cronograma_page(request: Request):
    return templates.TemplateResponse(request=request, name="agua/cronograma.html", context={"current_page": "cronograma"})

@router.get("/validacao", response_class=HTMLResponse)
async def get_validacao_page(request: Request):
    return templates.TemplateResponse(request=request, name="agua/validacao.html", context={"current_page": "validacao"})

@router.get("/planejamento", response_class=HTMLResponse)
async def get_planejamento_page(request: Request):
    return templates.TemplateResponse(request=request, name="agua/planejamento.html", context={"current_page": "planejamento"})

@router.get("/pedreiros", response_class=HTMLResponse)
async def get_pedreiros_page(request: Request):
    return templates.TemplateResponse(request=request, name="agua/pedreiros.html", context={"current_page": "pedreiros"})
