from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth.dependencies import get_current_user
from app.modules.agua_que_alimenta.models import CronogramaItem, CronogramaItemBase
from app.core.database import get_supabase

router = APIRouter(prefix="/api/cronograma", tags=["Cronograma"])

@router.get("", response_model=List[CronogramaItem])
def listar_itens_cronograma():
    try:
        supabase = get_supabase()
        res = supabase.table('cronograma').select('*').order('data_prevista', desc=False).execute()
        itens = []
        for row in (res.data or []):
            row['data_prevista'] = str(row.get('data_prevista', ''))
            row['data_realizada'] = str(row.get('data_realizada', '')) if row.get('data_realizada') else None
            itens.append(CronogramaItem(**row))
        return itens
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cronograma: {e}")


@router.get("/{item_id}", response_model=CronogramaItem)
def get_item_cronograma_por_id(item_id: int):
    try:
        supabase = get_supabase()
        res = supabase.table('cronograma').select('*').eq('id', item_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Item não encontrado")
            
        row = res.data[0]
        row['data_prevista'] = str(row.get('data_prevista', ''))
        row['data_realizada'] = str(row.get('data_realizada', '')) if row.get('data_realizada') else None
        return CronogramaItem(**row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar item do cronograma: {e}")


@router.post("", response_model=CronogramaItem, status_code=201)
def criar_item_cronograma(
    item: CronogramaItemBase,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        dados = item.dict()
        dados['data_prevista'] = str(dados.get('data_prevista', ''))
        if dados.get('data_realizada'):
            dados['data_realizada'] = str(dados.get('data_realizada', ''))
            
        res = supabase.table('cronograma').insert(dados).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Erro ao criar item no banco.")
            
        row = res.data[0]
        row['data_prevista'] = str(row.get('data_prevista', ''))
        row['data_realizada'] = str(row.get('data_realizada', '')) if row.get('data_realizada') else None
        return CronogramaItem(**row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar item: {e}")


@router.put("/{item_id}", response_model=CronogramaItem)
def atualizar_item_cronograma(
    item_id: int,
    item: CronogramaItemBase,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_old = supabase.table('cronograma').select('id').eq('id', item_id).execute()
        if not res_old.data:
            raise HTTPException(status_code=404, detail="Item não encontrado")
            
        dados = item.dict()
        dados['data_prevista'] = str(dados.get('data_prevista', ''))
        if dados.get('data_realizada'):
            dados['data_realizada'] = str(dados.get('data_realizada', ''))

        res_up = supabase.table('cronograma').update(dados).eq('id', item_id).execute()
        
        if not res_up.data:
            raise HTTPException(status_code=500, detail="Erro ao atualizar item.")
            
        row = res_up.data[0]
        row['data_prevista'] = str(row.get('data_prevista', ''))
        row['data_realizada'] = str(row.get('data_realizada', '')) if row.get('data_realizada') else None
        return CronogramaItem(**row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar item: {e}")

