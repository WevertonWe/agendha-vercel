from fastapi import APIRouter
from typing import Dict, Any
from app.core.database import fetch_all

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/resumo", response_model=Dict[str, Any])
async def get_dashboard_summary():
    """
    Retorna métricas consolidadas para o Dashboard Executivo.
    - BSF: Visitas Realizadas vs Meta Total
    - AQA: Total de Beneficiários Cadastrados
    - Financeiro: Total Executado
    - Ofícios: Total de Ofícios Registrados
    - Biomas: Consolidação dos Biomas (Soma Real)
    """
    # 1. BSF: Visitas Realizadas vs Meta
    visitas = fetch_all('bsf_visitas')
    bsf_realizado = len([v for v in visitas if str(v.get('status') or '').strip().lower() == 'realizada'])
    
    metas_contrato = fetch_all('bsf_metas_contrato')
    bsf_meta = sum(int(row.get('meta_anual') or 0) for row in metas_contrato if row.get('ano') == 2025)
    
    bsf_percent = 0.0
    if bsf_meta > 0:
        bsf_percent = round((bsf_realizado / bsf_meta) * 100, 1)
        
    # 2. AQA: Total Beneficiários
    beneficiarios = fetch_all('beneficiarios')
    aqa_total = len(beneficiarios)
    
    # 3. Financeiro: Total Executado (Todos os projetos)
    lancamentos = fetch_all('financeiro_lancamentos')
    financeiro_total = sum(float(row.get('valor') or 0.0) for row in lancamentos)
    
    # 4. Ofícios: Total Registrados
    oficios = fetch_all('oficios')
    oficios_total = len(oficios)
    
    # 5. Biomas: Consolidação
    projetos = fetch_all('financeiro_projetos')
    biomas_ids = []
    for p in projetos:
        nome = str(p.get('nome') or '').lower()
        proj_id = str(p.get('id') or '').lower()
        if 'biomas' in nome or 'biomas' in proj_id or 'ca-13' in proj_id or 'ca-24' in proj_id:
            biomas_ids.append(p.get('id'))
            
    biomas_financeiro = sum(float(lan.get('valor') or 0.0) for lan in lancamentos if lan.get('projeto_id') in biomas_ids)
    
    # Beneficiários dos biomas (tentativa de filtro por projeto)
    biomas_beneficiarios = 0
    try:
        biomas_beneficiarios = len([b for b in beneficiarios if str(b.get('projeto_id') or '') in biomas_ids or 'biomas' in str(b.get('projeto') or '').lower()])
    except Exception:
        biomas_beneficiarios = 0
        
    return {
        "bsf": {
            "realizado": int(bsf_realizado),
            "meta": int(bsf_meta),
            "percent": float(bsf_percent)
        },
        "aqa": {
            "beneficiarios": int(aqa_total)
        },
        "financeiro": {
            "executado": float(financeiro_total)
        },
        "oficios": {
            "total": int(oficios_total)
        },
        "biomas": {
            "financeiro_executado": float(biomas_financeiro),
            "beneficiarios": int(biomas_beneficiarios)
        }
    }

