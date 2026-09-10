import pandas as pd
import unicodedata, re

def norm(text):
    if not text: return ""
    nfkd = unicodedata.normalize('NFKD', str(text))
    s = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub(r'[^A-Z0-9]', '', s.upper())

df_col = pd.read_csv("coletum_caracterizacao_05_2026.csv", sep=";")
col_migson = df_col[df_col['tecnico'].str.contains('Migson', na=False)].copy()
print(f"Total de registros do Migson no Coletum em 05/2026: {len(col_migson)}")

df_pas = pd.read_csv("auditoria_pastas_ateste_coletum_geral.csv", sep=";")
pas_migson_m05 = df_pas[(df_pas['tecnico'] == 'migson') & (df_pas['pasta_atividade'].str.upper().str.contains('CARACTERI')) & (df_pas['mes_ano'] == '05/2026')].copy()
print(f"Total de pastas do Migson em 05/2026: {len(pas_migson_m05)}")
print("Status das pastas do Migson em 05/2026:")
print(pas_migson_m05['status'].value_counts())

# Vamos verificar os nomes
col_names = set(col_migson['beneficiario'].apply(norm))
pas_names = set(pas_migson_m05['beneficiario'].apply(norm))

nao_na_pasta = col_names - pas_names
print(f"\nNo Coletum do Migson mas não na pasta 05/2026 ({len(nao_na_pasta)}):")
for n in nao_na_pasta:
    print(" -", n)

nao_no_coletum = pas_names - col_names
print(f"\nNa pasta 05/2026 do Migson mas não no Coletum ({len(nao_no_coletum)}):")
for n in nao_no_coletum:
    print(" -", n)
