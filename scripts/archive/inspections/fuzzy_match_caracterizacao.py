import pandas as pd
from difflib import SequenceMatcher
import unicodedata, re

def norm(text):
    if not text: return ""
    nfkd = unicodedata.normalize('NFKD', str(text))
    s = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub(r'[^A-Z0-9]', '', s.upper())

df_col = pd.read_csv("coletum_caracterizacao_05_2026.csv", sep=";")
df_pas = pd.read_csv("auditoria_pastas_ateste_coletum_geral.csv", sep=";")
c_pas = df_pas[(df_pas['pasta_atividade'].str.upper().str.contains('CARACTERI')) & (df_pas['mes_ano'] == '05/2026')].copy()

col_records = df_col.to_dict('records')
pas_records = c_pas.to_dict('records')

matches = []
matched_pas_idx = set()

for c in col_records:
    c_ben = norm(c['beneficiario'])
    best_p = None
    best_ratio = 0.0
    best_idx = None
    
    for idx, p in enumerate(pas_records):
        p_ben = norm(p['beneficiario'])
        ratio = SequenceMatcher(None, c_ben, p_ben).ratio()
        if c_ben in p_ben or p_ben in c_ben:
            ratio = max(ratio, 0.95)
        if ratio > best_ratio:
            best_ratio = ratio
            best_p = p
            best_idx = idx
            
    if best_ratio >= 0.75:
        matched_pas_idx.add(best_idx)
        matches.append({
            'coletum_id': c['answer_id'],
            'coletum_ben': c['beneficiario'],
            'coletum_cpf': c['cpf'],
            'coletum_data': c['data_ativ'],
            'coletum_tec': c['tecnico'],
            'pasta_ben': best_p['beneficiario'],
            'pasta_tec': best_p['tecnico'],
            'pasta_com': best_p['comunidade'],
            'pasta_nome': best_p['pasta_atividade'],
            'status_pasta': best_p['status'],
            'tem_ateste': best_p['tem_ateste'],
            'tem_coletum': best_p['tem_coletum'],
            'ratio': round(best_ratio, 2)
        })
    else:
        matches.append({
            'coletum_id': c['answer_id'],
            'coletum_ben': c['beneficiario'],
            'coletum_cpf': c['cpf'],
            'coletum_data': c['data_ativ'],
            'coletum_tec': c['tecnico'],
            'pasta_ben': 'NÃO ENCONTRADO',
            'pasta_tec': '-',
            'pasta_com': '-',
            'pasta_nome': '-',
            'status_pasta': 'SEM_PASTA',
            'tem_ateste': 'NÃO',
            'tem_coletum': 'NÃO',
            'ratio': 0
        })

df_matches = pd.DataFrame(matches)
print(f"Total Coletum mapeado com pastas: {len(df_matches)}")
print("\nStatus nas pastas:")
print(df_matches['status_pasta'].value_counts())

nao_mapeados_pasta = [p for idx, p in enumerate(pas_records) if idx not in matched_pas_idx]
print(f"\nPastas locais de 05/2026 que não foram ligadas ao Coletum de 05/2026: {len(nao_mapeados_pasta)}")
for p in nao_mapeados_pasta:
    print(f"  [{p['tecnico']}] {p['beneficiario']} | {p['comunidade']} | {p['pasta_atividade']} | Status: {p['status']}")

print("\n--- CASOS NO COLETUM QUE NÃO ESTÃO 'COMPLETO' NA PASTA ---")
pend = df_matches[df_matches['status_pasta'] != 'COMPLETO']
for idx, r in pend.iterrows():
    print(f"ID: {r['coletum_id']} | Beneficiário: {r['coletum_ben']} | Técnico: {r['coletum_tec']} | Pasta: {r['pasta_ben']} | Status Pasta: {r['status_pasta']}")

df_matches.to_csv("auditoria_caracterizacao_05_2026.csv", index=False, sep=";", encoding="utf-8-sig")
