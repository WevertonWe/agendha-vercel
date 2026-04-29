import logging
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from app.core.database import get_supabase, fetch_all
from app.core.auth.dependencies import get_current_user
from app.modules.fornecedores.models import Fornecedor, FornecedorCreate, FornecedorUpdate

router = APIRouter(prefix="/api/fornecedores", tags=["Fornecedores"])
logger = logging.getLogger(__name__)

# --- CRUD ---

@router.get("/", response_model=List[Fornecedor])
def listar_fornecedores():
    try:
        # Usando fetch_all para paginação recursiva segura
        registros = fetch_all('fornecedores')
        
        # Mantendo ordenação por ID decrescente
        registros.sort(key=lambda x: x.get('id', 0), reverse=True)
        
        # Sanitização preventiva de datas para string
        for r in registros:
            for key in r.keys():
                if 'data' in key or 'updated' in key or 'created' in key:
                    r[key] = str(r[key]) if r[key] is not None else ''
                    
        return [Fornecedor(**r) for r in registros]
    except Exception as e:
        logger.error(f"Erro ao listar fornecedores: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar fornecedores.")

@router.post("/", response_model=Fornecedor, status_code=status.HTTP_201_CREATED)
def criar_fornecedor(
    fornecedor: FornecedorCreate,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        # Verificar duplicidade de CNPJ/CPF se fornecido
        if fornecedor.cnpj_cpf:
            res_check = supabase.table('fornecedores').select('id').eq('cnpj_cpf', fornecedor.cnpj_cpf).execute()
            if res_check.data:
                raise HTTPException(status_code=400, detail="CNPJ/CPF já cadastrado.")

        dados = fornecedor.dict(exclude_unset=True)
        res = supabase.table('fornecedores').insert(dados).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Erro ao salvar fornecedor no Supabase.")
            
        novo_registro = res.data[0]
        return Fornecedor(**novo_registro)

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao criar fornecedor: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar fornecedor.")

@router.put("/{id}", response_model=Fornecedor)
def atualizar_fornecedor(
    id: int,
    fornecedor: FornecedorUpdate,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_check = supabase.table('fornecedores').select('id').eq('id', id).execute()
        if not res_check.data:
            raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")

        dados = fornecedor.dict(exclude_unset=True)
        res = supabase.table('fornecedores').update(dados).eq('id', id).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Erro ao atualizar fornecedor no Supabase.")
            
        return Fornecedor(**res.data[0])

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao atualizar fornecedor: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar.")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_fornecedor(
    id: int,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_check = supabase.table('fornecedores').select('id').eq('id', id).execute()
        if not res_check.data:
            raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")

        supabase.table('fornecedores').delete().eq('id', id).execute()

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao deletar fornecedor: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar.")
