import logging
from datetime import timedelta, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.services.utils import remover_acentos
from app.modules.planejamento.schemas import (
    CronogramaExecucaoBase, 
    CronogramaUpdate, 
    SchemaGeracao
)

router = APIRouter(tags=["Planejamento e Cronograma"])

# --- TABELA AUTOMÁTICA & MIGRAÇÃO ---
# --- ROTAS ---

@router.post("/api/planejamento/item", status_code=201)
def criar_item_planejamento(
    dados: CronogramaExecucaoBase
):
    from app.core.database import get_supabase
    supabase = get_supabase()
    try:
        payload = dados.dict()
        res = supabase.table('cronograma_execucao').insert(payload).execute()
        if not res.data:
            raise HTTPException(status_code=500, detail="Erro ao criar item no Supabase.")
        return {"message": "Item criado com sucesso", "id": res.data[0]['id']}
    except Exception as e:
        logging.error(f"Erro ao criar item no Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar item: {e}")

@router.delete("/api/planejamento/item/{id}", status_code=204)
def excluir_item_planejamento(
    id: int
):
    from app.core.database import get_supabase
    supabase = get_supabase()
    try:
        supabase.table('cronograma_execucao').delete().eq('id', id).execute()
    except Exception as e:
        logging.error(f"Erro ao excluir item no Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir item: {e}")

@router.put("/api/planejamento/item/{id}")
def atualizar_item_planejamento(
    id: int,
    dados: CronogramaUpdate
):
    from app.core.database import get_supabase
    supabase = get_supabase()
    
    try:
        res_current = supabase.table('cronograma_execucao').select('*').eq('id', id).execute()
        if not res_current.data:
            raise HTTPException(status_code=404, detail="Item não encontrado")
            
        current = res_current.data[0]
        
        new_semana = dados.semana_referencia if dados.semana_referencia is not None else current['semana_referencia']
        new_quant = dados.quant_cisternas if dados.quant_cisternas is not None else current.get('quant_cisternas', 0)
        new_meta = dados.meta_planejada if dados.meta_planejada is not None else current['meta_planejada']
        new_exec = dados.qtd_executada if dados.qtd_executada is not None else current['qtd_executada']
        
        payload = {
            "semana_referencia": new_semana,
            "quant_cisternas": new_quant,
            "meta_planejada": new_meta,
            "qtd_executada": new_exec
        }
        
        supabase.table('cronograma_execucao').update(payload).eq('id', id).execute()
        return {"message": "Item atualizado"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erro ao atualizar item no Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {e}")

@router.delete("/api/planejamento/limpar-tudo/{municipio}")
def limpar_cronograma_municipio(
    municipio: str
):
    from app.core.database import get_supabase
    supabase = get_supabase()
    try:
        supabase.table('cronograma_execucao').delete().eq('municipio', municipio).execute()
        return {"message": "Cronograma limpo com sucesso"}
    except Exception as e:
        logging.error(f"Erro ao limpar cronograma no Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao limpar: {e}")

@router.post("/api/planejamento/gerar-automatico/{municipio}")
def gerar_cronograma_automatico(
    municipio: str,
    dados: SchemaGeracao
):
    from app.core.database import get_supabase
    supabase = get_supabase()
    
    try:
        supabase.table('cronograma_execucao').delete().eq('municipio', municipio).execute()
        
        saldo_atual = dados.total_cisternas
        
        try:
            data_atual = datetime.strptime(dados.data_inicio, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
            
        payloads = []
        while saldo_atual > 0:
            meta_real = min(dados.meta_semanal, saldo_atual)
            
            payloads.append({
                "municipio": municipio,
                "semana_referencia": data_atual.strftime("%Y-%m-%d"),
                "quant_cisternas": saldo_atual,
                "meta_planejada": meta_real,
                "qtd_executada": 0
            })
            
            saldo_atual -= meta_real
            data_atual += timedelta(days=7)
            
        if payloads:
            supabase.table('cronograma_execucao').insert(payloads).execute()
            
        return {"message": "Cronograma gerado com sucesso!"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erro ao gerar cronograma no Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar cronograma: {e}")

# --- BENEFICIÁRIOS LINKING ---

@router.get("/api/planejamento/beneficiarios/busca")
def buscar_beneficiarios_para_vinculo(
    q: str,
    municipio: Optional[str] = None
):
    if not q or len(q) < 3:
        return []
    
    from app.core.database import get_supabase
    supabase = get_supabase()
    
    try:
        import re
        q_clean = q.strip().upper()
        q_digits = re.sub(r'[^0-9]', '', q)
        
        query = supabase.table('beneficiarios').select('id, nome_completo, cpf, status, municipio')
        
        if len(q_digits) > 5:
            query = query.ilike('cpf', f"%{q_digits}%")
        else:
            query = query.ilike('nome_completo', f"%{q_clean}%")
            
        if municipio:
            query = query.eq('municipio', remover_acentos(municipio).upper())
            
        res = query.limit(10).execute()
        return res.data or []
        
    except Exception as e:
        logging.error(f"Erro ao buscar beneficiários no Supabase: {e}")
        return []

@router.post("/api/planejamento/vincular")
def vincular_beneficiario(
    dados: dict
):
    cronograma_id = dados.get('cronograma_id')
    beneficiario_id = dados.get('beneficiario_id')
    pedreiro_id = dados.get('pedreiro_id')
    data_execucao = dados.get('data_execucao')
    
    if not cronograma_id or not beneficiario_id:
        raise HTTPException(status_code=400, detail="IDs obrigatórios")
        
    from app.core.database import get_supabase
    supabase = get_supabase()

    try:
        res_dup = supabase.table('cronograma_beneficiarios').select('id').eq('cronograma_id', cronograma_id).eq('beneficiario_id', beneficiario_id).execute()
        if res_dup.data:
            return {"message": "Já vinculado"}
            
        supabase.table('cronograma_beneficiarios').insert({
            "cronograma_id": cronograma_id,
            "beneficiario_id": beneficiario_id,
            "pedreiro_id": pedreiro_id,
            "data_execucao": data_execucao
        }).execute()
        
        supabase.table('beneficiarios').update({
            "status": 'CONSTRUÍDA',
            "status_pagamento": 'PENDENTE',
            "pedreiro_id": pedreiro_id,
            "data_conclusao": data_execucao
        }).eq('id', beneficiario_id).execute()
        
        return {"message": "Vínculo criado"}
        
    except Exception as e:
        logging.error(f"Erro ao vincular no Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao vincular: {e}")

@router.delete("/api/planejamento/desvincular")
def desvincular_beneficiario(
    cronograma_id: int, 
    beneficiario_id: int
):
    from app.core.database import get_supabase
    supabase = get_supabase()
    try:
        supabase.table('cronograma_beneficiarios').delete().eq('cronograma_id', cronograma_id).eq('beneficiario_id', beneficiario_id).execute()
        return {"message": "Vínculo removido"}
    except Exception as e:
        logging.error(f"Erro ao desvincular no Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao desvincular: {e}")
        cursor = db.cursor()
        cursor.execute("""
            DELETE FROM cronograma_beneficiarios 
            WHERE cronograma_id = ? AND beneficiario_id = ?
        """, (cronograma_id, beneficiario_id))
        db.commit()
        return {"message": "Vínculo removido"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao desvincular: {e}")

# --- UPDATE GET TO INCLUDE BENEFICIARIES ---

@router.get("/api/planejamento/{municipio}")
def listar_planejamento(
    municipio: str
):
    from app.core.database import get_supabase
    supabase = get_supabase()
    
    try:
        res_itens = supabase.table('cronograma_execucao').select('*').eq('municipio', municipio).order('semana_referencia', desc=False).execute()
        itens = res_itens.data or []

        if not itens:
            return []

        ids_cronograma = [item['id'] for item in itens]
        mapa_benefs = {}
        
        if ids_cronograma:
            res_vinculos = supabase.table('cronograma_beneficiarios').select('cronograma_id, beneficiario_id, pedreiro_id').in_('cronograma_id', ids_cronograma).execute()
            vinculos = res_vinculos.data or []
            
            if vinculos:
                ids_benefs = [v['beneficiario_id'] for v in vinculos]
                res_benefs = supabase.table('beneficiarios').select('id, nome_completo, status, doc_status').in_('id', ids_benefs).execute()
                benefs_dict = {b['id']: b for b in res_benefs.data} if res_benefs.data else {}
                
                for v in vinculos:
                    cid = v['cronograma_id']
                    bid = v['beneficiario_id']
                    benef_data = benefs_dict.get(bid)
                    
                    if benef_data:
                        doc_path = benef_data.get('doc_status', 'PENDENTE')
                        benef = {
                            "id": bid,
                            "nome_completo": benef_data.get('nome_completo', 'Não informado'),
                            "status": benef_data.get('status', 'IMPORTADO'),
                            "caminho_documento": doc_path,
                            "arquivo_caminho": doc_path
                        }
                        if cid not in mapa_benefs:
                            mapa_benefs[cid] = []
                        mapa_benefs[cid].append(benef)

        for item in itens:
            item['beneficiarios'] = mapa_benefs.get(item['id'], [])
            quant = item.get('quant_cisternas') or 0
            meta = item.get('meta_planejada') or 0
            item['saldo_acumulado'] = quant - meta

        return itens
            
    except Exception as e:
        logging.error(f"Erro ao listar planejamento no Supabase: {e}")
        return []
