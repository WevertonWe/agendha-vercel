import pandas as pd
import unicodedata, re

def norm(text):
    if not text: return ""
    nfkd = unicodedata.normalize('NFKD', str(text))
    s = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub(r'[^A-Z0-9]', '', s.upper())

df_col = pd.read_csv("coletum_caracterizacao_05_2026.csv", sep=";")
df_pas = pd.read_csv("auditoria_pastas_ateste_coletum_geral.csv", sep=";")
c_pas = df_pas[(df_pas['pasta_atividade'].str.upper().str.contains('CARACTERI')) & (df_pas['mes_ano'] == '05/2026')].copy()

df_col['ben_norm'] = df_col['beneficiario'].apply(norm)
c_pas['ben_norm'] = c_pas['beneficiario'].apply(norm)

print(f"Total Coletum 05/2026: {len(df_col)}")
print(f"Total Pastas 05/2026: {len(c_pas)}")

# Cruzamento
merged = pd.merge(df_col, c_pas, on='ben_norm', how='outer', suffixes=('_coletum', '_pasta'))
print(f"Total combinado: {len(merged)}")

print("\n--- RESUMO DO STATUS NAS PASTAS DOS 51 DO COLETUM ---")
print(merged['status'].value_counts(dropna=False))

print("\n--- CASOS ESPECIAIS (NÃO COMPLETOS OU COM DIVERGÊNCIA) ---")
for idx, r in merged[merged['status'] != 'COMPLETO'].iterrows():
    print(f"Ben: {r['beneficiario_coletum'] or r['beneficiario_pasta']} | Tec Coletum: {r['tecnico_coletum']} | Tec Pasta: {r['tecnico_pasta']} | Status Pasta: {r['status']} | AnsID: {r['answer_id']}")
