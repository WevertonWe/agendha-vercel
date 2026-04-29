import os
from typing import List, Dict, Any
from supabase import create_client
from app.modules.financeiro.models import (
    FinanceiroProjetoBase, FinanceiroMetaBase, FinanceiroEtapaBase, FinanceiroRubricaBase, FinanceiroEntidadeBase, FinanceiroLancamentoBase
)

def get_supabase():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    return create_client(supabase_url, supabase_key)

def create_projeto(projeto: FinanceiroProjetoBase) -> int:
    supabase = get_supabase()
    res = supabase.table('financeiro_projetos').insert(projeto.dict()).execute()
    return res.data[0]['id'] if res.data else None

def create_meta(meta: FinanceiroMetaBase) -> int:
    supabase = get_supabase()
    res = supabase.table('financeiro_metas').insert(meta.dict()).execute()
    return res.data[0]['id'] if res.data else None

def create_etapa(etapa: FinanceiroEtapaBase) -> int:
    supabase = get_supabase()
    res = supabase.table('financeiro_etapas').insert(etapa.dict()).execute()
    return res.data[0]['id'] if res.data else None

def create_rubrica(rubrica: FinanceiroRubricaBase) -> int:
    supabase = get_supabase()
    data = rubrica.dict()
    if data.get('valor_total_programado') is None and data.get('quantidade_programada') and data.get('valor_unitario_programado'):
        data['valor_total_programado'] = data['quantidade_programada'] * data['valor_unitario_programado']
    res = supabase.table('financeiro_rubricas').insert(data).execute()
    return res.data[0]['id'] if res.data else None

def create_entidade(entidade: FinanceiroEntidadeBase) -> int:
    supabase = get_supabase()
    res = supabase.table('financeiro_entidades').insert(entidade.dict()).execute()
    return res.data[0]['id'] if res.data else None

def create_lancamento(lancamento: FinanceiroLancamentoBase) -> int:
    supabase = get_supabase()
    res = supabase.table('financeiro_lancamentos').insert(lancamento.dict()).execute()
    return res.data[0]['id'] if res.data else None

def get_projeto_completo(projeto_id: int) -> Dict[str, Any]:
    supabase = get_supabase()
    
    # 1. Get Projeto
    res_proj = supabase.table('financeiro_projetos').select('*').eq('id', projeto_id).execute()
    if not res_proj.data:
        return None
    projeto = res_proj.data[0]
    projeto['metas'] = []

    # 2. Get Metas
    res_metas = supabase.table('financeiro_metas').select('*').eq('projeto_id', projeto_id).execute()
    for meta in res_metas.data:
        meta['etapas'] = []
        
        # 3. Get Etapas
        res_etapas = supabase.table('financeiro_etapas').select('*').eq('meta_id', meta['id']).execute()
        for etapa in res_etapas.data:
            etapa['rubricas'] = []
            
            # 4. Get Rubricas
            res_rubricas = supabase.table('financeiro_rubricas').select('*').eq('etapa_id', etapa['id']).execute()
            for rubrica in res_rubricas.data:
                # 5. Calculate Executed Value
                res_exec = supabase.table('financeiro_lancamentos').select('valor_total_executado').eq('rubrica_id', rubrica['id']).execute()
                valor_executado = sum(float(row.get('valor_total_executado', 0)) for row in res_exec.data) if res_exec.data else 0.0
                
                rubrica['valor_executado'] = valor_executado
                rubrica['saldo'] = (rubrica.get('valor_total_programado') or 0) - valor_executado
                etapa['rubricas'].append(rubrica)
            
            meta['etapas'].append(etapa)
        projeto['metas'].append(meta)
        
    return projeto

def list_entidades(limit: int = 5) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    res = supabase.table('financeiro_entidades').select('*').order('id', desc=True).limit(limit).execute()
    
    data = res.data if res.data else []
    for row in data:
        for k in row.keys():
            if 'data' in k or 'created' in k or 'status' in k:
                row[k] = str(row[k]) if row[k] is not None else ''
            elif row[k] is None:
                row[k] = ''
    return data

def get_all_entidades() -> List[Dict[str, Any]]:
    supabase = get_supabase()
    res = supabase.table('financeiro_entidades').select('id', 'nome_razao_social').order('nome_razao_social').execute()
    return res.data

def get_rubricas_flat(projeto_id: int) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    res_metas = supabase.table('financeiro_metas').select('id, numero_meta, descricao').eq('projeto_id', projeto_id).execute()
    meta_ids = [m['id'] for m in res_metas.data]
    if not meta_ids:
        return []
        
    res_etapas = supabase.table('financeiro_etapas').select('id, meta_id, numero_etapa, descricao').in_('meta_id', meta_ids).execute()
    etapa_ids = [e['id'] for e in res_etapas.data]
    if not etapa_ids:
        return []
        
    res_rubricas = supabase.table('financeiro_rubricas').select('id, etapa_id, codigo, descricao').in_('etapa_id', etapa_ids).execute()
    
    meta_map = {m['id']: m for m in res_metas.data}
    etapa_map = {e['id']: e for e in res_etapas.data}
    
    rubricas_flat = []
    for r in res_rubricas.data:
        etapa = etapa_map.get(r['etapa_id'], {})
        meta = meta_map.get(etapa.get('meta_id'), {})
        full_name = f"Meta {meta.get('numero_meta', '?')} > Etapa {etapa.get('numero_etapa', '?')} > {r['codigo']} - {r['descricao']}"
        rubricas_flat.append({
            "id": r['id'],
            "full_name": full_name
        })
    return rubricas_flat

def list_lancamentos(limit: int = 5) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    res = supabase.table('financeiro_lancamentos').select('*').order('id', desc=True).limit(limit).execute()
    
    if not res.data:
        return []
        
    entidade_ids = list(set(row['entidade_id'] for row in res.data if row.get('entidade_id')))
    rubrica_ids = list(set(row['rubrica_id'] for row in res.data if row.get('rubrica_id')))
    
    entidades_map = {}
    if entidade_ids:
        res_ent = supabase.table('financeiro_entidades').select('id', 'nome_razao_social').in_('id', entidade_ids).execute()
        entidades_map = {e['id']: e['nome_razao_social'] for e in res_ent.data}
        
    rubricas_map = {}
    if rubrica_ids:
        res_rub = supabase.table('financeiro_rubricas').select('id', 'descricao').in_('id', rubrica_ids).execute()
        rubricas_map = {r['id']: r['descricao'] for r in res_rub.data}
        
    for row in res.data:
        row['nome_razao_social'] = entidades_map.get(row.get('entidade_id'), 'Desconhecido')
        row['rubrica_descricao'] = rubricas_map.get(row.get('rubrica_id'), 'Desconhecido')
        # Forçando tipos para evitar erros no template
        row['data_lancamento'] = str(row.get('data_lancamento') or '')
        row['status'] = str(row.get('status') or '')
        row['valor'] = float(row.get('valor') or 0.0)
        
    return res.data

def get_lancamento(lancamento_id: int) -> Dict[str, Any]:
    supabase = get_supabase()
    res = supabase.table('financeiro_lancamentos').select('*').eq('id', lancamento_id).execute()
    if not res.data:
        return None
    
    lancamento = res.data[0]
    
    # Forçando tipos para evitar erros no template
    lancamento['data_lancamento'] = str(lancamento.get('data_lancamento') or '')
    lancamento['status'] = str(lancamento.get('status') or '')
    lancamento['valor'] = float(lancamento.get('valor') or 0.0)
    
    if lancamento.get('entidade_id'):
        res_ent = supabase.table('financeiro_entidades').select('*').eq('id', lancamento['entidade_id']).execute()
        if res_ent.data:
            lancamento.update({
                "nome_razao_social": res_ent.data[0].get('nome_razao_social'),
                "cpf_cnpj": res_ent.data[0].get('cpf_cnpj')
            })
            
    if lancamento.get('rubrica_id'):
        res_rub = supabase.table('financeiro_rubricas').select('codigo', 'descricao').eq('id', lancamento['rubrica_id']).execute()
        if res_rub.data:
            lancamento.update({
                "rubrica_codigo": res_rub.data[0].get('codigo'),
                "rubrica_descricao": res_rub.data[0].get('descricao')
            })
            
    if lancamento.get('projeto_id'):
        res_proj = supabase.table('financeiro_projetos').select('nome', 'numero_contrato').eq('id', lancamento['projeto_id']).execute()
        if res_proj.data:
            lancamento.update({
                "projeto_name": res_proj.data[0].get('nome'),
                "numero_contrato": res_proj.data[0].get('numero_contrato')
            })
            
    return lancamento

def get_dashboard_data() -> List[Dict[str, Any]]:
    supabase = get_supabase()
    res_proj = supabase.table('financeiro_projetos').select('*').order('id', desc=True).execute()
    
    dashboard_data = []
    for row in res_proj.data:
        projeto = row
        projeto_id = projeto['id']
        
        res_metas = supabase.table('financeiro_metas').select('id').eq('projeto_id', projeto_id).execute()
        meta_ids = [m['id'] for m in res_metas.data]
        
        total_orcado = 0.0
        if meta_ids:
            res_etapas = supabase.table('financeiro_etapas').select('id').in_('meta_id', meta_ids).execute()
            etapa_ids = [e['id'] for e in res_etapas.data]
            if etapa_ids:
                res_rubricas = supabase.table('financeiro_rubricas').select('valor_total_programado').in_('etapa_id', etapa_ids).execute()
                total_orcado = sum(float(r.get('valor_total_programado', 0)) for r in res_rubricas.data) if res_rubricas.data else 0.0
                
        res_exec = supabase.table('financeiro_lancamentos').select('valor_total_executado').eq('projeto_id', projeto_id).execute()
        total_executado = sum(float(l.get('valor_total_executado', 0)) for l in res_exec.data) if res_exec.data else 0.0
        
        saldo = total_orcado - total_executado
        percentual_concluido = 0.0
        if total_orcado > 0:
            percentual_concluido = (total_executado / total_orcado) * 100
            
        projeto['total_orcado'] = total_orcado
        projeto['total_executado'] = total_executado
        projeto['saldo'] = saldo
        projeto['percentual_concluido'] = round(percentual_concluido, 2)
        
        dashboard_data.append(projeto)
        
    return dashboard_data

def get_extrato_projeto(projeto_id: int) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    res = supabase.table('financeiro_lancamentos').select('*').eq('projeto_id', projeto_id).order('data_lancamento', desc=True).execute()
    
    if not res.data:
        return []
        
    entidade_ids = list(set(row['entidade_id'] for row in res.data if row.get('entidade_id')))
    rubrica_ids = list(set(row['rubrica_id'] for row in res.data if row.get('rubrica_id')))
    
    entidades_map = {}
    if entidade_ids:
        res_ent = supabase.table('financeiro_entidades').select('id', 'nome_razao_social').in_('id', entidade_ids).execute()
        entidades_map = {e['id']: e['nome_razao_social'] for e in res_ent.data}
        
    rubricas_map = {}
    if rubrica_ids:
        res_rub = supabase.table('financeiro_rubricas').select('id', 'codigo', 'descricao').in_('id', rubrica_ids).execute()
        rubricas_map = {r['id']: {"codigo": r['codigo'], "descricao": r['descricao']} for r in res_rub.data}
        
    for row in res.data:
        row['nome_razao_social'] = entidades_map.get(row.get('entidade_id'), 'Desconhecido')
        rubrica = rubricas_map.get(row.get('rubrica_id'), {})
        row['rubrica_codigo'] = rubrica.get('codigo', 'N/A')
        row['rubrica_descricao'] = rubrica.get('descricao', 'Desconhecido')
        # Forçando tipos para evitar erros no template
        row['data_lancamento'] = str(row.get('data_lancamento') or '')
        row['status'] = str(row.get('status') or '')
        row['valor'] = float(row.get('valor') or 0.0)
        
    return res.data

def update_projeto(projeto_id: int, data: Dict[str, Any]) -> bool:
    supabase = get_supabase()
    res = supabase.table('financeiro_projetos').update(data).eq('id', projeto_id).execute()
    return len(res.data) > 0

def delete_projeto(projeto_id: int) -> bool:
    supabase = get_supabase()
    supabase.table('financeiro_lancamentos').delete().eq('projeto_id', projeto_id).execute()
    
    res_metas = supabase.table('financeiro_metas').select('id').eq('projeto_id', projeto_id).execute()
    meta_ids = [m['id'] for m in res_metas.data]
    if meta_ids:
        res_etapas = supabase.table('financeiro_etapas').select('id').in_('meta_id', meta_ids).execute()
        etapa_ids = [e['id'] for e in res_etapas.data]
        if etapa_ids:
            supabase.table('financeiro_rubricas').delete().in_('etapa_id', etapa_ids).execute()
            supabase.table('financeiro_etapas').delete().in_('meta_id', meta_ids).execute()
            
    supabase.table('financeiro_metas').delete().eq('projeto_id', projeto_id).execute()
    res = supabase.table('financeiro_projetos').delete().eq('id', projeto_id).execute()
    return len(res.data) > 0

def get_entidade(entidade_id: int) -> Dict[str, Any]:
    supabase = get_supabase()
    res = supabase.table('financeiro_entidades').select('*').eq('id', entidade_id).execute()
    return res.data[0] if res.data else None

def update_entidade(entidade_id: int, data: Dict[str, Any]) -> bool:
    supabase = get_supabase()
    res = supabase.table('financeiro_entidades').update(data).eq('id', entidade_id).execute()
    return len(res.data) > 0

def delete_entidade(entidade_id: int) -> bool:
    supabase = get_supabase()
    res = supabase.table('financeiro_entidades').delete().eq('id', entidade_id).execute()
    return len(res.data) > 0

def update_lancamento(lancamento_id: int, data: Dict[str, Any]) -> bool:
    supabase = get_supabase()
    res = supabase.table('financeiro_lancamentos').update(data).eq('id', lancamento_id).execute()
    return len(res.data) > 0

def delete_lancamento(lancamento_id: int) -> bool:
    supabase = get_supabase()
    res = supabase.table('financeiro_lancamentos').delete().eq('id', lancamento_id).execute()
    return len(res.data) > 0

def get_rubrica(rubrica_id: int) -> Dict[str, Any]:
    supabase = get_supabase()
    res = supabase.table('financeiro_rubricas').select('*').eq('id', rubrica_id).execute()
    return res.data[0] if res.data else None

def update_rubrica(rubrica_id: int, data: Dict[str, Any]) -> bool:
    supabase = get_supabase()
    if 'quantidade_programada' in data and 'valor_unitario_programado' in data:
        data['valor_total_programado'] = data['quantidade_programada'] * data['valor_unitario_programado']
    res = supabase.table('financeiro_rubricas').update(data).eq('id', rubrica_id).execute()
    return len(res.data) > 0

def delete_rubrica(rubrica_id: int) -> bool:
    supabase = get_supabase()
    res = supabase.table('financeiro_rubricas').delete().eq('id', rubrica_id).execute()
    return len(res.data) > 0
