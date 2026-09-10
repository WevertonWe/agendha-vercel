import pandas as pd

# Verificar pastas da Cristina em 05/2026
df_pas = pd.read_csv('auditoria_pastas_ateste_coletum_geral.csv', sep=';')
cris_m05 = df_pas[(df_pas['tecnico'] == 'cristina') & (df_pas['mes_ano'] == '05/2026')]
print(f"Total de atividades da Cristina em 05/2026 nas pastas: {len(cris_m05)}")
for idx, r in cris_m05.iterrows():
    print(f"  {r['comunidade']} | {r['beneficiario']} | {r['pasta_atividade']} | Status: {r['status']}")

# Verificar se Cristina tem alguma Caracterização no Coletum
df_col_caract = pd.read_csv('coletum_caracterizacao_todas.csv', sep=';')
cris_col = df_col_caract[df_col_caract['tecnico'].str.contains('Cristina', na=False, case=False)]
print(f"\nTotal de Caracterizações da Cristina no Coletum: {len(cris_col)}")
for idx, r in cris_col.iterrows():
    print(f"  {r['answer_id']} | {r['comunidade']} | {r['beneficiario']} | Data: {r['data_ativ']}")
