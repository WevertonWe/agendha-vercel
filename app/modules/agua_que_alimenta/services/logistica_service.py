import sqlite3
from typing import List, Dict, Any

# Fallback se sklearn não estiver instalado
try:
    from sklearn.cluster import KMeans
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

def get_abare_candidates(db: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Retorna beneficiários de Abaré elegíveis para os eventos logísticos.
    Critério:
    1. Município deve começar com 'ABAR' (Abaré).
    2. Campo GRH deve estar vazio ou não ser 'GRH %' (i.e. ainda não atendidos).
    
    Retorna lista de dicionários (rows).
    """
    cursor = db.cursor()
    query = """
        SELECT * FROM beneficiarios 
        WHERE UPPER(municipio) LIKE 'ABAR%' 
        AND (grh IS NULL OR grh = '' OR grh NOT LIKE 'GRH %')
    """
    cursor.execute(query)
    return [dict(row) for row in cursor.fetchall()]

def calculate_logistics_preview(db: sqlite3.Connection):
    """
    Calcula uma prévia logística para os 3 eventos planejados.
    
    Etapas:
    1. Separa candidatos com e sem coordenadas GPS.
    2. Aplica K-Means (se disponível) ou divisão simples para agrupar em 3 clusters geográficos.
    3. Distribui candidatos sem GPS via Round-Robin.
    4. Estima custos de Alimentação (R$ 35/pessoa) e Diárias da Equipe (R$ 600/evento).
    
    Retorna um dicionário com o resumo, grupos e custos totais.
    """
    candidates = get_abare_candidates(db)
    
    if not candidates:
        return {
            "timestamp": "Agora",
            "total_candidatos": 0,
            "grupos": [],
            "custo_total_estimado": 0.0,
            "resumo": "Nenhum candidato elegível encontrado.",
            "parametros": {}
        }

    # 1. Separar com e sem coordenadas
    com_coords = []
    sem_coords = []
    
    for c in candidates:
        try:
            lat = float(str(c['latitude']).replace(',', '.'))
            lon = float(str(c['longitude']).replace(',', '.'))
            if lat != 0 and lon != 0:
                c['_lat'] = lat
                c['_lon'] = lon
                com_coords.append(c)
            else:
                sem_coords.append(c)
        except (ValueError, TypeError):
            sem_coords.append(c)

    # 2. Agrupamento (Clustering)
    grupos = {0: [], 1: [], 2: []} # Evento 1, 2, 3
    
    if HAS_SKLEARN and len(com_coords) >= 3:
        # K-Means Clustering
        coords = np.array([[c['_lat'], c['_lon']] for c in com_coords])
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        labels = kmeans.fit_predict(coords)
        
        for i, c in enumerate(com_coords):
            grupos[labels[i]].append(c)
            
        # Centroids para "Sem Coordenadas"
        centroids = kmeans.cluster_centers_
    else:
        # Fallback Simples: Divisão por lista (simplesmente divide em 3 fatias)
        # TODO: Melhorar heurística de comunidade se necessário
        chunk_size = (len(com_coords) // 3) + 1
        for i, c in enumerate(com_coords):
            g_idx = min(i // chunk_size, 2)
            grupos[g_idx].append(c)
        centroids = None  # noqa: F841

    # 3. Alocar "Sem Coordenadas" (Pela Comunidade ou Round Robin)
    # Por simplicidade/performance: Round Robin nos 3 grupos para balancear carga
    idx_rr = 0
    for c in sem_coords:
        grupos[idx_rr % 3].append(c)
        idx_rr += 1

    # 4. Cálculo de Custos (Modelo Macururé - Alimentação + Diárias)
    # Alimentação (Café + Almoço) por pessoa
    # Ref: Frango, Carne, Cesta Café
    COST_FEEDING_PERSON = 35.00 
    
    # Diárias (2 Técnicos * 2 Dias)
    # Ref: R$ 150.00 por diária
    COST_STAFF_EVENT = 2 * 2 * 150.00 # R$ 600.00
    
    resumo_grupos = []
    total_geral = 0
    
    for i in range(3):
        qtd = len(grupos[i])
        
        # Custos
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
                "kits": custo_alimentacao, # Mantendo chave 'kits' para compatibilidade frontend temporária, mas semanticamente é Alimentação
                "logistica": custo_equipe  # Semanticamente é Equipe/Logística
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
