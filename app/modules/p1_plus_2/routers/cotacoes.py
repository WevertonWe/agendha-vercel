import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.core.database import get_supabase, fetch_all, db_insert, db_update, db_delete
from app.modules.p1_plus_2.models import (
    CotacaoP12MasterCreate, CotacaoP12MasterUpdate, CotacaoP12ItemBase
)


router = APIRouter(prefix="/api/p1-2/cotacoes", tags=["P1+2 - Cotações"])
logger = logging.getLogger(__name__)

@router.get("")
async def listar_cotacoes(status: Optional[str] = None):
    try:
        master = fetch_all("p12_cotacoes_master")
        itens = fetch_all("p12_cotacao_itens")
        
        if status and status != "TODOS":
            master = [m for m in master if str(m.get("status") or "").lower() == status.lower()]
            
        for m in master:
            m_id = m.get("id")
            m_itens = [it for it in itens if it.get("cotacao_master_id") == m_id]
            m["itens"] = m_itens
            m["total_itens"] = len(m_itens)
            total = sum(float(it.get("valor_total_estimado") or 0.0) for it in m_itens)
            m["valor_total"] = total
            m["valor_total_estimado"] = total
            
        master.sort(key=lambda x: str(x.get("created_at") or x.get("data_abertura") or ""), reverse=True)
        return {"total": len(master), "dados": master}
    except Exception as e:
        logger.error(f"Erro ao listar cotações P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/{id}")
async def obter_cotacao(id: int):
    try:
        master_list = fetch_all("p12_cotacoes_master")
        master = next((m for m in master_list if m.get("id") == id), None)
        if not master:
            raise HTTPException(status_code=404, detail="Cotação não encontrada.")
        
        itens = fetch_all("p12_cotacao_itens")
        m_itens = [it for it in itens if it.get("cotacao_master_id") == id]
        master["itens"] = m_itens
        master["total_itens"] = len(m_itens)
        total = sum(float(it.get("valor_total_estimado") or 0.0) for it in m_itens)
        master["valor_total"] = total
        master["valor_total_estimado"] = total
        return master
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter cotação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter: {e}")

@router.post("", status_code=201)
async def criar_cotacao(payload: CotacaoP12MasterCreate):
    try:
        dados_master = {
            "codigo_cotacao": payload.codigo_cotacao,
            "titulo": payload.titulo,
            "descricao": payload.descricao or "",
            "status": payload.status or "Aberta"
        }

        novo = db_insert("p12_cotacoes_master", dados_master)
        novo_id = novo["id"]
        
        if payload.itens:
            for item in payload.itens:
                item_dict = item.dict()
                item_dict["cotacao_master_id"] = novo_id
                qtd = float(item_dict.get("quantidade") or 1)
                val_un = float(item_dict.get("valor_unitario_estimado") or 0.0)
                item_dict["valor_total_estimado"] = qtd * val_un
                db_insert("p12_cotacao_itens", item_dict)
                
        return {"message": "Cotação criada com sucesso!", "id": novo_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar cotação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar: {e}")

@router.put("/{id}")
async def atualizar_cotacao(id: int, payload: CotacaoP12MasterUpdate):
    try:
        dados_master = {}
        if payload.codigo_cotacao is not None:
            dados_master["codigo_cotacao"] = payload.codigo_cotacao
        if payload.titulo is not None:
            dados_master["titulo"] = payload.titulo
        if payload.descricao is not None:
            dados_master["descricao"] = payload.descricao
        if payload.status is not None:
            dados_master["status"] = payload.status

        if dados_master:
            db_update("p12_cotacoes_master", id, dados_master)
            
        if payload.itens is not None:
            try:
                db_delete("p12_cotacao_itens", id, id_col="cotacao_master_id")
            except Exception:
                pass
            for item in payload.itens:
                item_dict = item.dict()
                item_dict["cotacao_master_id"] = id
                qtd = float(item_dict.get("quantidade") or 1)
                val_un = float(item_dict.get("valor_unitario_estimado") or 0.0)
                item_dict["valor_total_estimado"] = qtd * val_un
                db_insert("p12_cotacao_itens", item_dict)

        return {"message": "Cotação atualizada com sucesso!"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar cotação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {e}")

@router.delete("/{id}")
async def excluir_cotacao(id: int):
    try:
        try:
            db_delete("p12_cotacao_itens", id, id_col="cotacao_master_id")
        except Exception:
            pass
        db_delete("p12_cotacoes_master", id)
        return {"message": "Cotação excluída com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao excluir cotação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir: {e}")