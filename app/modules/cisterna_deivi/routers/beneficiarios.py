import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.core.database import fetch_all, db_insert, db_update, db_delete
from app.modules.cisterna_deivi.models import (
    BeneficiarioCisterna, BeneficiarioCisternaCreate, BeneficiarioCisternaUpdate
)
from app.services.utils import remover_acentos

router = APIRouter(prefix="/api/cisterna-deivi/beneficiarios", tags=["Cisterna Deivi - Beneficiários"])
logger = logging.getLogger(__name__)

TABLE_NAME = "cisterna_beneficiarios"

@router.get("", response_model=dict)
async def listar_beneficiarios(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = None,
    municipio: Optional[str] = None,
    comunidade: Optional[str] = None
):
    try:
        dados = fetch_all(TABLE_NAME)
        
        # Filtro de Busca Geral (Nome, CPF, Comunidade)
        if search:
            s_clean = search.lower().strip()
            s_num = "".join(filter(str.isdigit, search))
            dados = [
                d for d in dados if
                (d.get("nome_completo") and s_clean in str(d["nome_completo"]).lower()) or
                (s_num and s_num in "".join(filter(str.isdigit, str(d.get("cpf") or "")))) or
                (d.get("comunidade") and s_clean in str(d["comunidade"]).lower()) or
                (d.get("municipio") and s_clean in str(d["municipio"]).lower())
            ]

        # Filtro de Município
        if municipio and municipio != "TODOS":
            m_norm = remover_acentos(municipio).lower()
            dados = [d for d in dados if d.get("municipio") and remover_acentos(str(d["municipio"])).lower() == m_norm]

        # Filtro de Comunidade
        if comunidade and comunidade != "TODOS":
            c_norm = remover_acentos(comunidade).lower()
            dados = [d for d in dados if d.get("comunidade") and remover_acentos(str(d["comunidade"])).lower() == c_norm]

        # Ordenar alfabeticamente por nome
        dados.sort(key=lambda x: str(x.get("nome_completo") or "").upper())

        total = len(dados)
        start = (page - 1) * limit
        end = start + limit
        paginados = dados[start:end]

        # Listas para filtros no frontend
        todos_registros = fetch_all(TABLE_NAME)
        municipios = sorted(list(set([d.get("municipio") for d in todos_registros if d.get("municipio")])))
        comunidades = sorted(list(set([d.get("comunidade") for d in todos_registros if d.get("comunidade")])))

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            "itens": paginados,
            "municipios": municipios,
            "comunidades": comunidades
        }
    except Exception as e:
        logger.error(f"Erro ao listar beneficiários Cisterna Deivi: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Erro interno ao consultar beneficiários: {str(e)}", "itens": [], "total": 0}
        )


@router.get("/{beneficiario_id}")
async def obter_beneficiario(beneficiario_id: int):
    try:
        dados = fetch_all(TABLE_NAME)
        item = next((d for d in dados if int(d.get("id")) == beneficiario_id), None)
        if not item:
            raise HTTPException(status_code=404, detail="Beneficiário não encontrado.")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter beneficiário {beneficiario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", status_code=status.HTTP_201_CREATED)
async def criar_beneficiario(payload: BeneficiarioCisternaCreate):
    try:
        dados = payload.dict()
        novo = db_insert(TABLE_NAME, dados)
        return {"success": True, "message": "Beneficiário cadastrado com sucesso!", "data": novo}
    except Exception as e:
        logger.error(f"Erro ao cadastrar beneficiário Cisterna Deivi: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar beneficiário: {str(e)}")


@router.put("/{beneficiario_id}")
async def atualizar_beneficiario(beneficiario_id: int, payload: BeneficiarioCisternaUpdate):
    try:
        dados = {k: v for k, v in payload.dict().items() if v is not None}
        if not dados:
            return {"success": True, "message": "Nenhum campo para atualizar."}
        
        atualizado = db_update(TABLE_NAME, beneficiario_id, dados)
        return {"success": True, "message": "Beneficiário atualizado com sucesso!", "data": atualizado}
    except Exception as e:
        logger.error(f"Erro ao atualizar beneficiário {beneficiario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {str(e)}")


@router.delete("/{beneficiario_id}")
async def excluir_beneficiario(beneficiario_id: int):
    try:
        db_delete(TABLE_NAME, beneficiario_id)
        return {"success": True, "message": "Beneficiário removido com sucesso."}
    except Exception as e:
        logger.error(f"Erro ao excluir beneficiário {beneficiario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir: {str(e)}")
