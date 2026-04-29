import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth.dependencies import get_current_user
from app.modules.materiais.models import Material, MaterialCreate, MaterialUpdate
from app.core.database import get_supabase

router = APIRouter(prefix="/api/materiais", tags=["Materiais"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[Material])
def listar_materiais():
    try:
        supabase = get_supabase()
        res = supabase.table('materiais').select('*').order('nome').execute()
        return [Material(**dict(r)) for r in res.data]
    except Exception as e:
        logger.error(f"Erro ao listar materiais: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar materiais.")

@router.post("/", response_model=Material, status_code=status.HTTP_201_CREATED)
def criar_material(
    material: MaterialCreate,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        dados = material.dict(exclude_unset=True)
        res = supabase.table('materiais').insert(dados).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Erro ao salvar material no Supabase.")
            
        return Material(**dict(res.data[0]))

    except Exception as e:
        logger.error(f"Erro ao criar material: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar material.")

@router.put("/{id}", response_model=Material)
def atualizar_material(
    id: int,
    material: MaterialUpdate,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_old = supabase.table('materiais').select('id').eq('id', id).execute()
        if not res_old.data:
            raise HTTPException(status_code=404, detail="Material não encontrado.")

        dados = material.dict(exclude_unset=True)
        if not dados:
             raise HTTPException(status_code=400, detail="Nenhum campo para atualizar.")

        res_up = supabase.table('materiais').update(dados).eq('id', id).execute()
        
        if not res_up.data:
            raise HTTPException(status_code=500, detail="Erro ao atualizar material no Supabase.")

        return Material(**dict(res_up.data[0]))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar material: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar material.")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_material(
    id: int,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_old = supabase.table('materiais').select('id').eq('id', id).execute()
        if not res_old.data:
            raise HTTPException(status_code=404, detail="Material não encontrado.")

        supabase.table('materiais').delete().eq('id', id).execute()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar material: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar material.")

