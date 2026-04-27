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
    cursor = db.cursor()
    
    # 1. BSF: Visitas Realizadas vs Meta
    # Nota: A tabela bsf_visitas tem status. Consideramos apenas 'Realizada'.
    # A tabela bsf_metas tem meta_total por município/mês.
    
    # Visitas Realizadas (Total Geral)
    cursor.execute("SELECT COUNT(*) FROM bsf_visitas WHERE status = 'Realizada'")
    bsf_realizado = cursor.fetchone()[0] or 0
    
    # Meta Total (Soma de todas as metas cadastradas no sistema - simplificado para visão geral)
    # Se houver filtro de ano/mês no futuro, ajustar aqui. Por enquanto, visão acumulada.
    # Meta Total (Soma da meta anual do contrato ativo - 2025)
    # TODO: Tornar dinâmico com tabela de configuração de "Contrato Ativo"
    # Filtrando apenas atividades principais se necessário para atingir 15.350, mas seguindo a ordem de somar meta_anual.
    # A soma total atual no banco é 16276. O usuário espera 15350. 
    # Assumindo que a query deve ser fiel aos dados do banco.
    cursor.execute("SELECT SUM(meta_anual) FROM bsf_metas_contrato WHERE ano = 2025")
    bsf_meta = cursor.fetchone()[0] or 0
    
    bsf_percent = 0.0
    if bsf_meta > 0:
        bsf_percent = round((bsf_realizado / bsf_meta) * 100, 1)
        
    # 2. AQA: Total Beneficiários
    # Tabela: beneficiarios
    cursor.execute("SELECT COUNT(*) FROM beneficiarios")
    aqa_total = cursor.fetchone()[0] or 0
    
    # 3. Financeiro: Total Executado
    # Tabela: financeiro_lancamentos, coluna: valor_total_executado
    cursor.execute("SELECT SUM(valor_total_executado) FROM financeiro_lancamentos")
    financeiro_total = cursor.fetchone()[0] or 0.0
    
    # 4. Ofícios: Total Registrados
    # Tabela: oficios
    cursor.execute("SELECT COUNT(*) FROM oficios")
    oficios_total = cursor.fetchone()[0] or 0
    
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
