from fastapi import APIRouter, Depends
from app.core.database import get_db_connection
import sqlite3
from typing import Dict, Any

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/resumo", response_model=Dict[str, Any])
async def get_dashboard_summary(db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Retorna métricas consolidadas para o Dashboard Executivo.
    - BSF: Visitas Realizadas vs Meta Total (Soma de todas as metas ativas)
    - AQA: Total de Beneficiários Cadastrados
    - Financeiro: Total Executado (Soma de todos os lançamentos)
    - Ofícios: Total de Ofícios Registrados
    """
    import os
    from supabase import create_client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    supabase = create_client(supabase_url, supabase_key)
    
    # 1. BSF: Visitas Realizadas vs Meta
    res_realizado = supabase.table('bsf_visitas').select('count', count='exact').eq('status', 'Realizada').execute()
    bsf_realizado = res_realizado.count or 0
    
    res_meta = supabase.table('bsf_metas_contrato').select('meta_anual').eq('ano', 2025).execute()
    bsf_meta = sum(row.get('meta_anual', 0) for row in res_meta.data) if res_meta.data else 0
    
    bsf_percent = 0.0
    if bsf_meta > 0:
        bsf_percent = round((bsf_realizado / bsf_meta) * 100, 1)
        
    # 2. AQA: Total Beneficiários
    res_aqa = supabase.table('beneficiarios').select('count', count='exact').execute()
    aqa_total = res_aqa.count or 0
    
    # 3. Financeiro: Total Executado
    res_fin = supabase.table('financeiro_lancamentos').select('valor').execute()
    financeiro_total = sum(float(row.get('valor', 0)) for row in res_fin.data) if res_fin.data else 0.0
    
    # 4. Ofícios: Total Registrados
    res_oficios = supabase.table('oficios').select('count', count='exact').execute()
    oficios_total = res_oficios.count or 0
    
    return {
        "bsf": {
            "realizado": bsf_realizado,
            "meta": bsf_meta,
            "percent": bsf_percent
        },
        "aqa": {
            "beneficiarios": aqa_total
        },
        "financeiro": {
            "executado": financeiro_total
        },
        "oficios": {
            "total": oficios_total
        }
    }
