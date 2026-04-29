from typing import List, Optional
from app.core.database import get_supabase
from .models import PontoCreate, PontoResponse, CategoriaCreate, CategoriaResponse

def create_ponto(ponto: PontoCreate) -> Optional[PontoResponse]:
    try:
        supabase = get_supabase()
        dados = ponto.dict(exclude_unset=True)
        res = supabase.table('mapa_pontos').insert(dados).execute()
        
        if not res.data:
            return None
            
        ponto_dict = res.data[0]
        for k in ponto_dict.keys():
            if 'data' in k or 'created' in k or 'status' in k:
                ponto_dict[k] = str(ponto_dict[k]) if ponto_dict[k] is not None else ''
                
        return PontoResponse(**ponto_dict)
    except Exception as e:
        print(f"Erro ao criar ponto no Supabase: {e}")
        return None

def get_all_pontos(contexto: str = 'geral', responsavel: Optional[str] = None) -> List[PontoResponse]:
    try:
        supabase = get_supabase()
        query = supabase.table('mapa_pontos').select('*').eq('contexto', contexto)
        
        if responsavel:
            query = query.eq('responsavel', responsavel)
            
        res = query.order('id', desc=True).execute()
        
        pontos = []
        for row in (res.data or []):
            ponto_dict = dict(row)
            for k in ponto_dict.keys():
                if 'data' in k or 'created' in k or 'status' in k:
                    ponto_dict[k] = str(ponto_dict[k]) if ponto_dict[k] is not None else ''
            pontos.append(PontoResponse(**ponto_dict))
            
        return pontos
    except Exception as e:
        print(f"Erro ao buscar pontos no Supabase: {e}")
        return []

def delete_ponto(ponto_id: int) -> bool:
    try:
        supabase = get_supabase()
        res = supabase.table('mapa_pontos').delete().eq('id', ponto_id).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"Erro ao deletar ponto: {e}")
        return False

def get_ponto(ponto_id: int) -> Optional[PontoResponse]:
    try:
        supabase = get_supabase()
        res = supabase.table('mapa_pontos').select('*').eq('id', ponto_id).execute()
        
        if not res.data:
            return None
            
        ponto_dict = res.data[0]
        for k in ponto_dict.keys():
            if 'data' in k or 'created' in k or 'status' in k:
                ponto_dict[k] = str(ponto_dict[k]) if ponto_dict[k] is not None else ''
                
        return PontoResponse(**ponto_dict)
    except Exception as e:
        print(f"Erro ao buscar ponto {ponto_id}: {e}")
        return None

def update_ponto(ponto_id: int, ponto: PontoCreate) -> Optional[PontoResponse]:
    try:
        supabase = get_supabase()
        dados = ponto.dict(exclude_unset=True)
        res = supabase.table('mapa_pontos').update(dados).eq('id', ponto_id).execute()
        
        if not res.data:
            return None
            
        ponto_dict = res.data[0]
        for k in ponto_dict.keys():
            if 'data' in k or 'created' in k or 'status' in k:
                ponto_dict[k] = str(ponto_dict[k]) if ponto_dict[k] is not None else ''
                
        return PontoResponse(**ponto_dict)
    except Exception as e:
        print(f"Erro ao atualizar ponto {ponto_id}: {e}")
        return None

# --- Services de Categorias ---

def get_all_categorias() -> List[CategoriaResponse]:
    try:
        supabase = get_supabase()
        res = supabase.table('mapa_categorias').select('*').order('nome', desc=False).execute()
        
        return [CategoriaResponse(**dict(row)) for row in (res.data or [])]
    except Exception as e:
        print(f"Erro ao buscar categorias: {e}")
        return []

def create_categoria(categoria: CategoriaCreate) -> Optional[CategoriaResponse]:
    try:
        supabase = get_supabase()
        dados = categoria.dict(exclude_unset=True)
        res = supabase.table('mapa_categorias').insert(dados).execute()
        
        if not res.data:
            return None
            
        return CategoriaResponse(**res.data[0])
    except Exception as e:
        print(f"Erro ao criar categoria: {e}")
        return None

def update_categoria(id: int, categoria: CategoriaCreate) -> Optional[CategoriaResponse]:
    try:
        supabase = get_supabase()
        dados = categoria.dict(exclude_unset=True)
        res = supabase.table('mapa_categorias').update(dados).eq('id', id).execute()
        
        if not res.data:
            return None
            
        return CategoriaResponse(**res.data[0])
    except Exception as e:
        print(f"Erro ao atualizar categoria: {e}")
        return None

def delete_categoria(id: int) -> bool:
    try:
        supabase = get_supabase()
        res = supabase.table('mapa_categorias').delete().eq('id', id).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"Erro ao deletar categoria: {e}")
        return False
