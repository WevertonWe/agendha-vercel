from app.core.database import fetch_all

def get_biomas_summary():
    """
    Retorna métricas consolidadas de apoio para todos os projetos de Biomas.
    Busca dados financeiros e de beneficiários na nuvem com sanitização.
    """
    projetos = fetch_all('financeiro_projetos')
    lancamentos = fetch_all('financeiro_lancamentos')
    beneficiarios = fetch_all('beneficiarios')
    
    for dataset in [projetos, lancamentos, beneficiarios]:
        for row in dataset:
            for k in row.keys():
                if 'data' in k or 'created' in k or 'status' in k:
                    row[k] = str(row[k]) if row[k] is not None else ''
                elif row[k] is None:
                    row[k] = ''
                    
    biomas_ids = []
    for p in projetos:
        nome = str(p.get('nome') or '').lower()
        proj_id = str(p.get('id') or '').lower()
        if 'biomas' in nome or 'biomas' in proj_id or 'ca-13' in proj_id or 'ca-24' in proj_id:
            biomas_ids.append(p.get('id'))
            
    total_executado = sum(float(lan.get('valor') or 0.0) for lan in lancamentos if lan.get('projeto_id') in biomas_ids)
    
    total_beneficiarios = 0
    try:
        total_beneficiarios = len([b for b in beneficiarios if str(b.get('projeto_id') or '') in biomas_ids or 'biomas' in str(b.get('projeto') or '').lower()])
    except Exception:
        total_beneficiarios = 0
        
    return {
        "total_executado": total_executado,
        "total_beneficiarios": total_beneficiarios,
        "biomas_ids": biomas_ids
    }

def get_progresso_bioma(projeto_slug: str):
    """
    Retorna o progresso de um bioma específico (ex: ater-biomas-ca-13).
    """
    summary = get_biomas_summary()
    return {
        "slug": projeto_slug,
        "status": "Em Execução",
        "executado": summary["total_executado"],
        "beneficiarios": summary["total_beneficiarios"]
    }
