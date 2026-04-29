from typing import List, Dict, Any
from app.core.database import get_supabase

# Fallback se sklearn não estiver instalado
try:
    from sklearn.cluster import KMeans
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

def get_abare_candidates() -> List[Dict[str, Any]]:
    """
    Retorna beneficiários de Abaré elegíveis para os eventos logísticos via Supabase.
    """
    try:
        supabase = get_supabase()
        # Para fazer filtros complexos com OR no Supabase, ou fazemos .or_()
        # grh IS NULL OR grh = '' OR grh NOT LIKE 'GRH %'
        # Em vez de query complexa no OR, podemos trazer todos de Abaré e filtrar em Python para garantir
        res = supabase.table('beneficiarios').select('*').ilike('municipio', 'ABAR%').execute()
        
        candidates = []
        for row in (res.data or []):
            grh_val = str(row.get('grh') or '').strip()
            if not grh_val or not grh_val.startswith('GRH '):
                candidates.append(row)
        return candidates
    except Exception as e:
        print(f"Erro ao buscar candidatos de Abaré no Supabase: {e}")
        return []

def calculate_logistics_preview():
    """
    Calcula uma prévia logística para os 3 eventos planejados.
    """
    candidates = get_abare_candidates()
    
    if not candidates:
        return {
            "timestamp": "Agora",
            "total_candidatos": 0,
            "grupos": [],
            "custo_total_estimado": 0.0,
            "resumo": "Nenhum candidato elegível encontrado.",
            "parametros": {}
        }

    com_coords = []
    sem_coords = []
    
    for c in candidates:
        try:
            lat = float(str(c.get('latitude', '')).replace(',', '.'))
            lon = float(str(c.get('longitude', '')).replace(',', '.'))
            if lat != 0 and lon != 0:
                c['_lat'] = lat
                c['_lon'] = lon
                com_coords.append(c)
            else:
                sem_coords.append(c)
        except (ValueError, TypeError):
            sem_coords.append(c)

    grupos = {0: [], 1: [], 2: []} 
    
    if HAS_SKLEARN and len(com_coords) >= 3:
        coords = np.array([[c['_lat'], c['_lon']] for c in com_coords])
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        labels = kmeans.fit_predict(coords)
        
        for i, c in enumerate(com_coords):
            grupos[labels[i]].append(c)
            
        centroids = kmeans.cluster_centers_
    else:
        chunk_size = (len(com_coords) // 3) + 1
        for i, c in enumerate(com_coords):
            g_idx = min(i // chunk_size, 2)
            grupos[g_idx].append(c)
        centroids = None  # noqa: F841

    idx_rr = 0
    for c in sem_coords:
        grupos[idx_rr % 3].append(c)
        idx_rr += 1

    COST_FEEDING_PERSON = 35.00 
    COST_STAFF_EVENT = 2 * 2 * 150.00 
    
    resumo_grupos = []
    total_geral = 0
    
    for i in range(3):
        qtd = len(grupos[i])
        custo_alimentacao = qtd * COST_FEEDING_PERSON
        custo_equipe = COST_STAFF_EVENT
        
        subtotal = custo_alimentacao + custo_equipe
        total_geral += subtotal
        
        resumo_grupos.append({
            "grupo_id": i + 1,
            "nome_evento": f"Evento {i+1} (Capacitação)",
            "quantidade_beneficiarios": qtd,
            "beneficiarios": grupos[i], 
            "custo_estimado": subtotal,
            "detalhes_custo": {
                "kits": custo_alimentacao,
                "logistica": custo_equipe 
            }
        })

    return {
        "timestamp": "Agora",
        "total_candidatos": len(candidates),
        "grupos": resumo_grupos,
        "custo_total_estimado": total_geral,
        "parametros": {
            "custo_alimentacao_pessoa": COST_FEEDING_PERSON,
            "custo_equipe_evento": COST_STAFF_EVENT
        }
    }

