from app.core.database import get_supabase, fetch_all

def get_all_oficios(db=None):
    # Usando fetch_all para garantir a leitura total com paginação
    data = fetch_all('oficios')
    # Mantendo a ordenação por ID decrescente
    data.sort(key=lambda x: x.get('id', 0), reverse=True)
    return data


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

