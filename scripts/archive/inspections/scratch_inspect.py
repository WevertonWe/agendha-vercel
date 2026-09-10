import pandas as pd

df = pd.read_csv('auditoria_pastas_ateste_coletum_geral.csv', sep=';')
comp = df[df['status'] == 'COMPLETO']
print("EXEMPLOS DE ATIVIDADES COMPLETAS:")
for idx, row in comp.head(10).iterrows():
    print(f"Tecnico: {row['tecnico']} | Beneficiario: {row['beneficiario']} | Pasta: {row['pasta_atividade']}")
    print(f"   Ateste: {row['arquivos_ateste']}")
    print(f"   Coletum: {row['arquivos_coletum']}")

print("\nEXEMPLOS DE FALTA COLETUM (MÊS 08/2026):")
m08_falta = df[(df['mes_ano'] == '08/2026') & (df['status'] == 'FALTA_COLETUM')]
for idx, row in m08_falta.head(10).iterrows():
    print(f"Tecnico: {row['tecnico']} | Beneficiario: {row['beneficiario']} | Pasta: {row['pasta_atividade']}")
    print(f"   Ateste existente: {row['arquivos_ateste']}")
