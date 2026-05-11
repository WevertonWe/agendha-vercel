"""
BSF Beneficiários - API Router
Endpoints para listagem, filtros e preparação de arquivos do módulo BSF.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.database import get_supabase

router = APIRouter(prefix="/api/bsf/beneficiarios", tags=["BSF Beneficiários"])

logger = logging.getLogger(__name__)


@router.get("")
async def listar_beneficiarios(
    tecnico: Optional[str] = Query(None, description="Filtro por técnico responsável"),
    municipio: Optional[str] = Query(None, description="Filtro por município"),
    status: Optional[str] = Query(None, description="Filtro por status"),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(50, ge=1, le=200, description="Itens por página"),
):
    """Lista beneficiários com filtros opcionais por técnico e município."""
    try:
        supabase = get_supabase()
        
        cols = (
            "id, nome_completo, cpf, municipio, comunidade, "
            "nome_tecnico, tecnico_agua_que_alimenta, status, "
            "verificado_bsf, data_atividade"
        )
        
        query = supabase.table("beneficiarios").select(cols, count="exact")
        
        if tecnico:
            query = query.ilike("nome_tecnico", f"%{tecnico}%")
        if municipio:
            query = query.ilike("municipio", f"%{municipio}%")
        if status:
            query = query.ilike("status", f"%{status}%")
        
        # BSF filter: only verified beneficiaries if needed
        # query = query.not_.is_("verificado_bsf", "null")
        
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        query = query.order("id", desc=True)
        
        res = query.execute()
        
        total = res.count if res.count is not None else len(res.data or [])
        
        return {
            "data": res.data or [],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, -(-total // page_size)),
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar beneficiários BSF: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar beneficiários.")


@router.get("/filtros")
async def obter_filtros():
    """Retorna valores únicos de técnico e município para popular os selects de filtro."""
    try:
        supabase = get_supabase()
        
        # Fetch unique tecnicos
        res_tec = supabase.table("beneficiarios").select("nome_tecnico").not_.is_("nome_tecnico", "null").execute()
        tecnicos_raw = [r["nome_tecnico"] for r in (res_tec.data or []) if r.get("nome_tecnico")]
        tecnicos = sorted(set(t.strip() for t in tecnicos_raw if t.strip()))
        
        # Fetch unique municipios
        res_mun = supabase.table("beneficiarios").select("municipio").not_.is_("municipio", "null").execute()
        municipios_raw = [r["municipio"] for r in (res_mun.data or []) if r.get("municipio")]
        municipios = sorted(set(m.strip() for m in municipios_raw if m.strip()))
        
        # Fetch unique statuses
        res_st = supabase.table("beneficiarios").select("status").not_.is_("status", "null").execute()
        statuses_raw = [r["status"] for r in (res_st.data or []) if r.get("status")]
        statuses = sorted(set(s.strip() for s in statuses_raw if s.strip()))
        
        return {
            "tecnicos": tecnicos,
            "municipios": municipios,
            "statuses": statuses,
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter filtros BSF: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar filtros.")


@router.get("/{beneficiario_id}")
async def detalhar_beneficiario(beneficiario_id: int):
    """Retorna os dados completos de um beneficiário específico."""
    try:
        supabase = get_supabase()
        res = supabase.table("beneficiarios").select("*").eq("id", beneficiario_id).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Beneficiário não encontrado.")
        
        return res.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao detalhar beneficiário {beneficiario_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar beneficiário.")


@router.get("/{beneficiario_id}/arquivos")
async def listar_arquivos_beneficiario(beneficiario_id: int):
    """
    Prepara a estrutura de associação de arquivos para um beneficiário.
    Retorna os caminhos esperados para Sigater, Colletum e Ateste.
    """
    try:
        supabase = get_supabase()
        res = supabase.table("beneficiarios").select(
            "id, nome_completo, cpf, municipio"
        ).eq("id", beneficiario_id).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Beneficiário não encontrado.")
        
        ben = res.data[0]
        cpf_limpo = (ben.get("cpf") or "").replace(".", "").replace("-", "").replace(" ", "")
        municipio = (ben.get("municipio") or "SEM_MUNICIPIO").strip()
        
        # Storage path pattern for BSF documents
        base_path = f"bsf/{municipio}/{cpf_limpo}"
        
        arquivos = {
            "sigater": {
                "tipo": "Sigater",
                "path": f"{base_path}/sigater/",
                "descricao": "Relatório do Sistema de Gestão da Assistência Técnica",
                "arquivos_encontrados": [],
            },
            "colletum": {
                "tipo": "Colletum",
                "path": f"{base_path}/colletum/",
                "descricao": "Formulários de coleta de dados em campo",
                "arquivos_encontrados": [],
            },
            "ateste": {
                "tipo": "Ateste",
                "path": f"{base_path}/ateste/",
                "descricao": "Termos de ateste de atividades realizadas",
                "arquivos_encontrados": [],
            },
        }
        
        return {
            "beneficiario": ben,
            "storage_base": base_path,
            "documentos": arquivos,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar arquivos do beneficiário {beneficiario_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar arquivos.")
