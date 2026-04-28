import os
from supabase import create_client

def get_supabase():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    return create_client(supabase_url, supabase_key)

def get_all_oficios(db=None):
    supabase = get_supabase()
    res = supabase.table('oficios').select('*').order('id', desc=True).execute()
    return res.data

def create_oficio(db, dados: dict):
    supabase = get_supabase()
    payload = {
        "numero_oficio": dados.get('numero_oficio'),
        "destinatario": dados.get('destinatario'),
        "data_envio": dados.get('data_envio'),
        "motivo_descricao": dados.get('motivo_descricao'),
        "criado_por": dados.get('criado_por'),
        "caminho_arquivo": dados.get('caminho_arquivo')
    }
    res = supabase.table('oficios').insert(payload).execute()
    if res.data:
        return res.data[0].get('id')
    return None

def update_oficio(db, oficio_id: int, dados: dict):
    supabase = get_supabase()
    payload = {}
    
    for key in ['numero_oficio', 'destinatario', 'data_envio', 'motivo_descricao', 'caminho_arquivo']:
        if key in dados:
            payload[key] = dados[key]
            
    if not payload:
        return False
        
    res = supabase.table('oficios').update(payload).eq('id', oficio_id).execute()
    return len(res.data) > 0

def delete_oficio(db, oficio_id: int):
    supabase = get_supabase()
    res = supabase.table('oficios').delete().eq('id', oficio_id).execute()
    return len(res.data) > 0

