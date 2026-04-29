from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any
from jose import jwt, JWTError

from app.core.auth.utils import SECRET_KEY, ALGORITHM
from app.core.auth.models import UserInDB, UserProjectRole
from app.config import settings
from app.core.database import get_supabase

async def check_financeiro_access(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith(f"{settings.AUTH_BEARER_PREFIX} "):
            token = auth_header.split(" ")[1]

    if not token:
        print("BLOQUEADO: Acesso anônimo (sem token).")
        raise HTTPException(status_code=401, detail="Acesso não autorizado. Faça login.")

    try:
        if token.startswith(f"{settings.AUTH_BEARER_PREFIX} "):
            token = token.split(" ")[1]
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("BLOQUEADO: Token inválido (sem sub).")
            raise HTTPException(status_code=401, detail="Token inválido")
            
    except JWTError:
        print("BLOQUEADO: Token inválido ou expirado (JWTError).")
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    print(f"AUDITORIA: Usuário '{username}' tentando acessar Financeiro.")
    
    supabase = get_supabase()
    res = supabase.table('users').select('*').eq('username', username).execute()
    
    if not res.data:
        print(f"BLOQUEADO: Usuário '{username}' não encontrado no banco.")
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    user_dict = res.data[0]
    allowed_users = ['admin', 'marilac', 'mauricio', 'fabiano', 'valda']
    
    if user_dict['username'] not in allowed_users:
        print(f"BLOQUEADO: Usuário '{username}' não tem permissão.")
        raise HTTPException(status_code=403, detail="Acesso negado ao Módulo Financeiro")

    print(f"LIBERADO: Usuário '{username}' acessou Financeiro.")

    res_roles = supabase.table('user_project_roles').select('*').eq('user_id', user_dict['id']).execute()
    project_roles = [UserProjectRole(project_id=row['project_id'], role=row['role']) for row in res_roles.data or []]

    return UserInDB(
        username=user_dict['username'],
        full_name=user_dict['full_name'],
        role=user_dict['role'],
        is_active=bool(user_dict['is_active']),
        hashed_password=user_dict.get('password_hash', ''),
        project_roles=project_roles
    )


from app.modules.financeiro.models import (  # noqa: E402
    FinanceiroProjetoBase, FinanceiroMetaBase, FinanceiroEtapaBase, FinanceiroRubricaBase, FinanceiroEntidadeBase, FinanceiroLancamentoBase
)
from app.modules.financeiro import services  # noqa: E402

router = APIRouter(prefix="/financeiro", tags=["Financeiro"], dependencies=[Depends(check_financeiro_access)])

@router.post("/projetos", response_model=Dict[str, int])
def create_projeto_endpoint(projeto: FinanceiroProjetoBase):
    projeto_id = services.create_projeto(projeto)
    return {"id": projeto_id}

@router.put("/projetos/{projeto_id}")
def update_projeto_endpoint(projeto_id: int, projeto: FinanceiroProjetoBase):
    success = services.update_projeto(projeto_id, projeto.dict())
    if not success:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return {"message": "Projeto atualizado com sucesso"}

@router.delete("/projetos/{projeto_id}")
def delete_projeto_endpoint(projeto_id: int):
    success = services.delete_projeto(projeto_id)
    if not success:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return {"message": "Projeto excluído com sucesso"}

@router.post("/metas", response_model=Dict[str, int])
def create_meta_endpoint(meta: FinanceiroMetaBase):
    meta_id = services.create_meta(meta)
    return {"id": meta_id}

@router.post("/etapas", response_model=Dict[str, int])
def create_etapa_endpoint(etapa: FinanceiroEtapaBase):
    etapa_id = services.create_etapa(etapa)
    return {"id": etapa_id}

@router.post("/rubricas", response_model=Dict[str, int])
def create_rubrica_endpoint(rubrica: FinanceiroRubricaBase):
    rubrica_id = services.create_rubrica(rubrica)
    return {"id": rubrica_id}

@router.post("/entidades", response_model=Dict[str, int])
def create_entidade_endpoint(entidade: FinanceiroEntidadeBase):
    entidade_id = services.create_entidade(entidade)
    return {"id": entidade_id}

@router.get("/entidades", response_model=list[Dict[str, Any]])
def list_entidades_endpoint():
    return services.list_entidades()

@router.post("/lancamentos", response_model=Dict[str, int])
def create_lancamento_endpoint(lancamento: FinanceiroLancamentoBase):
    lancamento_id = services.create_lancamento(lancamento)
    return {"id": lancamento_id}

@router.get("/lancamentos/dados-formulario", response_model=Dict[str, Any])
def get_lancamento_form_data(projeto_id: int = 1): # Default to project 1 for now
    entidades = services.get_all_entidades()
    rubricas = services.get_rubricas_flat(projeto_id)
    return {
        "entidades": entidades,
        "rubricas": rubricas
    }

@router.get("/lancamentos", response_model=list[Dict[str, Any]])
def list_lancamentos_endpoint():
    return services.list_lancamentos()

@router.get("/projetos/{projeto_id}/plano", response_model=Dict[str, Any])
def get_projeto_plano_endpoint(projeto_id: int):
    projeto = services.get_projeto_completo(projeto_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return projeto

# --- Update/Delete Endpoints ---

@router.get("/entidades/{entidade_id}", response_model=Dict[str, Any])
def get_entidade_endpoint(entidade_id: int):
    entidade = services.get_entidade(entidade_id)
    if not entidade:
        raise HTTPException(status_code=404, detail="Entidade não encontrada")
    return entidade

@router.put("/entidades/{entidade_id}")
def update_entidade_endpoint(entidade_id: int, entidade: FinanceiroEntidadeBase):
    success = services.update_entidade(entidade_id, entidade.dict())
    if not success:
        raise HTTPException(status_code=404, detail="Entidade não encontrada")
    return {"message": "Entidade atualizada com sucesso"}

@router.delete("/entidades/{entidade_id}")
def delete_entidade_endpoint(entidade_id: int):
    success = services.delete_entidade(entidade_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entidade não encontrada")
    return {"message": "Entidade excluída com sucesso"}

@router.put("/lancamentos/{lancamento_id}")
def update_lancamento_endpoint(lancamento_id: int, lancamento: FinanceiroLancamentoBase):
    success = services.update_lancamento(lancamento_id, lancamento.dict())
    if not success:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    return {"message": "Lançamento atualizado com sucesso"}

@router.delete("/lancamentos/{lancamento_id}")
def delete_lancamento_endpoint(lancamento_id: int):
    success = services.delete_lancamento(lancamento_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    return {"message": "Lançamento excluído com sucesso"}

@router.get("/lancamentos/{lancamento_id}", response_model=Dict[str, Any])
def get_lancamento_endpoint(lancamento_id: int):
    lancamento = services.get_lancamento(lancamento_id)
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    return lancamento

@router.get("/projetos/{projeto_id}/extrato", response_model=list[Dict[str, Any]])
def get_projeto_extrato_endpoint(projeto_id: int):
    return services.get_extrato_projeto(projeto_id)

@router.get("/rubricas/{rubrica_id}", response_model=Dict[str, Any])
def get_rubrica_endpoint(rubrica_id: int):
    rubrica = services.get_rubrica(rubrica_id)
    if not rubrica:
        raise HTTPException(status_code=404, detail="Rubrica não encontrada")
    return rubrica

@router.put("/rubricas/{rubrica_id}")
def update_rubrica_endpoint(rubrica_id: int, rubrica: FinanceiroRubricaBase):
    success = services.update_rubrica(rubrica_id, rubrica.dict())
    if not success:
        raise HTTPException(status_code=404, detail="Rubrica não encontrada")
    return {"message": "Rubrica atualizada com sucesso"}

@router.delete("/rubricas/{rubrica_id}")
def delete_rubrica_endpoint(rubrica_id: int):
    success = services.delete_rubrica(rubrica_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rubrica não encontrada")
    return {"message": "Rubrica excluída com sucesso"}
