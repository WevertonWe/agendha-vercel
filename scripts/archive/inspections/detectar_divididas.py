import re
from pathlib import Path
from collections import defaultdict
from app.modules.bahia_sem_fome.services.auditoria_service import extrair_categoria_atividade

base_dir = Path(r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos")
ignorar = {'ATESTES', 'ATIVIDADES BAIXADAS', 'TEMP', 'UPLOADS'}

divididas = []

for tec in base_dir.iterdir():
    if not tec.is_dir() or tec.name.upper() in ignorar:
        continue
    doc_ativ = tec / "documentos-atividades"
    alvo = doc_ativ if doc_ativ.exists() else tec

    for com in alvo.iterdir():
        if not com.is_dir() or 'ATIVIDADE COLETIVA' in com.name.upper():
            continue
        for ben in com.iterdir():
            if not ben.is_dir():
                continue
            
            subdirs = [s for s in ben.iterdir() if s.is_dir()]
            por_cat = defaultdict(list)
            for s in subdirs:
                cat = extrair_categoria_atividade(s.name)
                pdfs = list(s.glob('*.pdf'))
                tem_at = any('ATEST' in f.name.upper() for f in pdfs)
                tem_col = any('COL' in f.name.upper() for f in pdfs)
                por_cat[cat].append({
                    'pasta': s.name,
                    'tem_ateste': tem_at,
                    'tem_coletum': tem_col,
                    'pdfs': [f.name for f in pdfs]
                })
            
            for cat, items in por_cat.items():
                if cat == 'OUTROS':
                    continue
                if len(items) > 1:
                    tem_at = any(it['tem_ateste'] for it in items)
                    tem_col = any(it['tem_coletum'] for it in items)
                    # Se uma tem ateste e outra tem coletum
                    if tem_at and tem_col and not all(it['tem_ateste'] and it['tem_coletum'] for it in items):
                        divididas.append({
                            'tecnico': tec.name,
                            'comunidade': com.name,
                            'beneficiario': ben.name,
                            'categoria': cat,
                            'pastas': items
                        })

print(f"Total de beneficiários com atividades complementares divididas: {len(divididas)}")
for d in divididas[:10]:
    print(f"\n{d['tecnico']} | {d['comunidade']} | {d['beneficiario']} - {d['categoria']}")
    for p in d['pastas']:
        print(f"   Pasta: {p['pasta']} (Ateste: {p['tem_ateste']}, Coletum: {p['tem_coletum']}, PDFs: {p['pdfs']})")
