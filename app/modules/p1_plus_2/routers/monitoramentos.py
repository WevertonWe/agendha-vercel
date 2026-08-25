import logging
import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.core.database import get_supabase, fetch_all, db_insert, db_update, db_delete
from app.modules.p1_plus_2.models import (
    MonitoramentoCreate, MonitoramentoUpdate
)

router = APIRouter(prefix="/api/p1-2/monitoramentos", tags=["P1+2 - Monitoramentos"])
logger = logging.getLogger(__name__)

@router.get("")
async def listar_monitoramentos(
    tipo: Optional[str] = Query(None, description="GAPA, SISMA, INTERCAMBIO ou TODOS"),
    search: Optional[str] = None
):
    try:
        dados = fetch_all("p12_monitoramentos")
        
        if tipo and tipo.upper() != "TODOS":
            t_clean = tipo.upper().strip()
            if t_clean == "INTERCÂMBIO":
                t_clean = "INTERCAMBIO"
            dados = [d for d in dados if str(d.get("tipo") or "").upper() == t_clean]
            
        if search:
            s_clean = search.lower().strip()
            dados = [
                d for d in dados if
                (d.get("titulo") and s_clean in str(d["titulo"]).lower()) or
                (d.get("municipio") and s_clean in str(d["municipio"]).lower()) or
                (d.get("comunidade") and s_clean in str(d["comunidade"]).lower()) or
                (d.get("responsavel") and s_clean in str(d["responsavel"]).lower())
            ]
            
        # Ordenar pelos mais recentes
        dados.sort(key=lambda x: str(x.get("data_evento") or ""), reverse=True)
        return {"total": len(dados), "dados": dados}
    except Exception as e:
        logger.error(f"Erro ao listar monitoramentos P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/participantes-disponiveis")
async def listar_participantes_disponiveis():
    try:
        beneficiarios = fetch_all("p12_beneficiarios")
        lista = []
        for b in beneficiarios:
            nome = b.get("nome_completo") or b.get("nome_familiar") or f"Beneficiário #{b.get('id')}"
            cpf = b.get("cpf") or b.get("cpf_familiar") or ""
            lista.append({
                "id": b.get("id"),
                "nome": nome,
                "cpf": cpf,
                "municipio": b.get("municipio"),
                "comunidade": b.get("comunidade")
            })
        return lista
    except Exception as e:
        logger.error(f"Erro ao listar participantes: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/{id}")
async def obter_monitoramento(id: int):
    try:
        dados = fetch_all("p12_monitoramentos")
        item = next((d for d in dados if d.get("id") == id), None)
        if not item:
            raise HTTPException(status_code=404, detail="Monitoramento não encontrado")
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", status_code=201)
async def criar_monitoramento(payload: MonitoramentoCreate):
    try:
        import datetime
        data_dict = payload.dict()
        if not data_dict.get("data_evento"):
            data_dict["data_evento"] = datetime.date.today().isoformat()
        novo = db_insert("p12_monitoramentos", data_dict)
        return {"message": "Monitoramento registrado com sucesso!", "dados": novo}
    except Exception as e:
        logger.error(f"Erro ao criar monitoramento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar: {e}")


@router.put("/{id}")
async def atualizar_monitoramento(id: int, payload: MonitoramentoUpdate):
    try:
        data_dict = {k: v for k, v in payload.dict().items() if v is not None}
        atualizado = db_update("p12_monitoramentos", id, data_dict)
        return {"message": "Monitoramento atualizado com sucesso!", "dados": atualizado}
    except Exception as e:
        logger.error(f"Erro ao atualizar monitoramento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {e}")

@router.delete("/{id}")
async def excluir_monitoramento(id: int):
    try:
        db_delete("p12_monitoramentos", id)
        return {"message": "Monitoramento excluído com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao excluir monitoramento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir: {e}")