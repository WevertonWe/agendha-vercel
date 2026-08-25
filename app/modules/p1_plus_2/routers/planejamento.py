import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.core.database import get_supabase, fetch_all, db_insert, db_update, db_delete
from app.modules.p1_plus_2.models import (
    CronogramaP12ItemBase, CronogramaP12ItemUpdate
)

router = APIRouter(prefix="/api/p1-2/planejamento", tags=["P1+2 - Planejamento"])
logger = logging.getLogger(__name__)

@router.get("")
async def listar_planejamento(municipio: Optional[str] = None):
    try:
        dados = fetch_all("p12_cronograma_execucao")
        if municipio and municipio != "TODOS":
            dados = [d for d in dados if str(d.get("municipio") or "").lower() == municipio.lower()]
        dados.sort(key=lambda x: (x.get("municipio", ""), x.get("semana_referencia", 0)))
        
        # Municípios únicos
        mun_unicos = sorted(list(set([d.get("municipio") for d in fetch_all("p12_cronograma_execucao") if d.get("municipio")])))
        
        total_meta = sum(int(d.get("meta_planejada") or 0) for d in dados)
        total_exec = sum(int(d.get("qtd_executada") or 0) for d in dados)
        percentual = round((total_exec / total_meta * 100), 1) if total_meta > 0 else 0.0
        
        return {
            "total_itens": len(dados),
            "meta_total": total_meta,
            "executado_total": total_exec,
            "percentual": percentual,
            "municipios": mun_unicos,
            "dados": dados
        }
    except Exception as e:
        logger.error(f"Erro ao listar planejamento P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.post("", status_code=201)
async def criar_item_planejamento(payload: CronogramaP12ItemBase):
    try:
        novo = db_insert("p12_cronograma_execucao", payload.dict())
        return {"message": "Meta semanal adicionada com sucesso!", "dados": novo}
    except Exception as e:
        logger.error(f"Erro ao criar meta de planejamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar: {e}")

@router.put("/{id}")
async def atualizar_item_planejamento(id: int, payload: CronogramaP12ItemUpdate):
    try:
        data_dict = {k: v for k, v in payload.dict().items() if v is not None}
        atualizado = db_update("p12_cronograma_execucao", id, data_dict)
        return {"message": "Meta atualizada com sucesso!", "dados": atualizado}
    except Exception as e:
        logger.error(f"Erro ao atualizar planejamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {e}")

@router.delete("/{id}")
async def excluir_item_planejamento(id: int):
    try:
        db_delete("p12_cronograma_execucao", id)
        return {"message": "Meta excluída com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao excluir meta: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir: {e}")

@router.post("/gerar-semanas")
async def gerar_semanas_municipio(municipio: str, qtd_semanas: int = 12, meta_por_semana: int = 5):
    try:
        itens = []
        for sem in range(1, qtd_semanas + 1):
            itens.append({
                "municipio": municipio,
                "semana_referencia": sem,
                "ano": 2026,
                "meta_planejada": meta_por_semana,
                "qtd_executada": 0,
                "status": "Planejado",
                "observacoes": f"Semana {sem}"
            })
        for it in itens:
            db_insert("p12_cronograma_execucao", it)
        return {"message": f"{qtd_semanas} semanas geradas para {municipio} com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao gerar semanas automáticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar: {e}")