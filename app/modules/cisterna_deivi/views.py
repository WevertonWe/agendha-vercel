import logging
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.database import fetch_all
from app.core.auth.utils import get_user_context_from_request

router = APIRouter(prefix="/cisterna-deivi", tags=["Cisterna Deivi - Views"])
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="app/templates")
TABLE_NAME = "cisterna_beneficiarios"

async def get_user_context(request: Request):
    return get_user_context_from_request(request, default_context_project="cisterna_deivi")

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
@router.get("/beneficiarios", response_class=HTMLResponse)
async def view_beneficiarios(request: Request):
    """Tela principal de Gestão de Beneficiários do Projeto Cisterna Deivi."""
    ctx = await get_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="cisterna_deivi/beneficiarios.html",
        context={
            "current_page": "cisterna_beneficiarios",
            **ctx
        }
    )


@router.get("/termos/recibo-construcao/{beneficiario_id}", response_class=HTMLResponse)
async def view_termo_recibo_construcao(beneficiario_id: int, request: Request):
    """Gera o Recibo de Contribuição à Família (Construção 16m³ e Cozinheira - R$ 1.180,00)."""
    ctx = await get_user_context(request)
    dados = fetch_all(TABLE_NAME)
    beneficiario = next((d for d in dados if int(d.get("id")) == beneficiario_id), None)
    if not beneficiario:
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado.")

    data_hoje = datetime.now()
    meses = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    data_formatada = {
        "dia": f"{data_hoje.day:02d}",
        "mes": meses[data_hoje.month],
        "ano": str(data_hoje.year)
    }

    return templates.TemplateResponse(
        request=request,
        name="cisterna_deivi/termos/recibo_construcao.html",
        context={
            "beneficiario": beneficiario,
            "data_formatada": data_formatada,
            **ctx
        }
    )


@router.get("/termos/recibo-agua/{beneficiario_id}", response_class=HTMLResponse)
async def view_termo_recibo_agua(beneficiario_id: int, request: Request):
    """Gera o Recibo de Contribuição à Família (Água para Abastecimento e Cura - R$ 200,00)."""
    ctx = await get_user_context(request)
    dados = fetch_all(TABLE_NAME)
    beneficiario = next((d for d in dados if int(d.get("id")) == beneficiario_id), None)
    if not beneficiario:
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado.")

    data_hoje = datetime.now()
    meses = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    data_formatada = {
        "dia": f"{data_hoje.day:02d}",
        "mes": meses[data_hoje.month],
        "ano": str(data_hoje.year)
    }

    return templates.TemplateResponse(
        request=request,
        name="cisterna_deivi/termos/recibo_agua.html",
        context={
            "beneficiario": beneficiario,
            "data_formatada": data_formatada,
            **ctx
        }
    )


@router.get("/termos/termo-coordenacao/{beneficiario_id}", response_class=HTMLResponse)
async def view_termo_coordenacao(beneficiario_id: int, request: Request):
    """Gera o Termo de Entrega e Compromisso com Assinatura da Coordenadora Geral Luciene Marilac."""
    ctx = await get_user_context(request)
    dados = fetch_all(TABLE_NAME)
    beneficiario = next((d for d in dados if int(d.get("id")) == beneficiario_id), None)
    if not beneficiario:
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado.")

    data_hoje = datetime.now()
    meses = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    data_formatada = {
        "dia": f"{data_hoje.day:02d}",
        "mes": meses[data_hoje.month],
        "ano": str(data_hoje.year)
    }

    return templates.TemplateResponse(
        request=request,
        name="cisterna_deivi/termos/termo_coordenacao.html",
        context={
            "beneficiario": beneficiario,
            "data_formatada": data_formatada,
            **ctx
        }
    )
