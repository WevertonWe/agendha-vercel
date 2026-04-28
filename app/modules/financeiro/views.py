from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.modules.financeiro import services
from app.modules.financeiro.routes import check_financeiro_access

# Adjust path to point to the correct templates directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env))

def date_br_filter(value):
    if not value:
        return ""
    try:
        from datetime import datetime
        if isinstance(value, str):
            date_obj = datetime.strptime(value, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        return value.strftime('%d/%m/%Y')
    except:  # noqa: E722
        return value

def currency_filter(value):
    if value is None:
        value = 0
    try:
        return "R$ {:,.2f}".format(float(value)).replace(',', 'v').replace('.', ',').replace('v', '.')
    except:  # noqa: E722
        return value

templates.env.filters['date_br'] = date_br_filter
templates.env.filters['currency'] = currency_filter

router = APIRouter(prefix="/financeiro", tags=["Financeiro Views"], dependencies=[Depends(check_financeiro_access)])

@router.get("/painel", response_class=HTMLResponse)
async def financeiro_painel(request: Request):
    projetos = services.get_dashboard_data()
    
    # Calculate totals in backend
    total_carteira = sum(p.get('total_orcado', 0) or 0 for p in projetos)
    total_executado = sum(p.get('total_executado', 0) or 0 for p in projetos)
    projetos_ativos = len(projetos)
    
    return templates.TemplateResponse("financeiro/painel.html", {
        "request": request,
        "projetos": projetos,
        "total_carteira": total_carteira,
        "total_executado": total_executado,
        "projetos_ativos": projetos_ativos
    })

@router.get("/cadastros", response_class=HTMLResponse)
async def financeiro_cadastros(request: Request):
    return templates.TemplateResponse("financeiro/cadastros.html", {"request": request})

@router.get("/plano/{projeto_id}", response_class=HTMLResponse)
async def financeiro_plano(request: Request, projeto_id: int):
    projeto = services.get_projeto_completo(projeto_id)
    if not projeto:
        # For now, just return a 404 page or simple error
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    return templates.TemplateResponse("financeiro/plano_trabalho.html", {
        "request": request,
        "projeto": projeto
    })

@router.get("/projeto/{projeto_id}/lancamentos", response_class=HTMLResponse)
async def financeiro_lancamentos(request: Request, projeto_id: int):
    projeto = services.get_projeto_completo(projeto_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    return templates.TemplateResponse("financeiro/lancamentos.html", {
        "request": request,
        "projeto": projeto
    })

@router.get("/lancamento/{lancamento_id}/recibo", response_class=HTMLResponse)
async def financeiro_recibo(request: Request, lancamento_id: int):
    lancamento = services.get_lancamento(lancamento_id)
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    
    # Format date for display
    from datetime import datetime
    if lancamento.get('data_lancamento'):
        try:
            dt = datetime.strptime(lancamento['data_lancamento'], '%Y-%m-%d')
            lancamento['data_lancamento_formatada'] = dt.strftime('%d de %B de %Y')
            # Need locale for full month name? Python locale might not be set.
            # Simple mapping for safety if locale fails or is english
            meses = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            lancamento['data_lancamento_formatada'] = f"{dt.day} de {meses[dt.month]} de {dt.year}"
        except:  # noqa: E722
            lancamento['data_lancamento_formatada'] = lancamento['data_lancamento']

    return templates.TemplateResponse("financeiro/recibo.html", {
        "request": request,
        "lancamento": lancamento
    })

@router.get("/projeto/{projeto_id}/relatorios", response_class=HTMLResponse)
async def financeiro_relatorios(request: Request, projeto_id: int):
    projeto = services.get_projeto_completo(projeto_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
    lancamentos = services.get_extrato_projeto(projeto_id)
    
    return templates.TemplateResponse("financeiro/relatorios.html", {
        "request": request,
        "projeto": projeto,
        "lancamentos": lancamentos
    })
