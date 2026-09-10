import pandas as pd

df = pd.read_csv('auditoria_pastas_ateste_coletum_geral.csv', sep=';')
caract = df[df['pasta_atividade'].str.upper().str.contains('CARACTERI')]
c_m05 = caract[caract['mes_ano'] == '05/2026'].copy()

print(f"Total de pastas em 05/2026: {len(c_m05)}")
print("\nPor Técnico:")
print(c_m05['tecnico'].value_counts())

print("\nPor Técnico e Status:")
print(c_m05.groupby(['tecnico', 'status']).size())

print("\nLISTAGEM COMPLETA DOS 51 BENEFICIÁRIOS EM 05/2026:")
cols = ['tecnico', 'comunidade', 'beneficiario', 'pasta_atividade', 'status', 'arquivos_ateste', 'arquivos_coletum']
for idx, r in c_m05[cols].reset_index().iterrows():
    print(f"{idx+1:02d}. [{r['tecnico']}] {r['beneficiario']} | Com: {r['comunidade']} | Pasta: {r['pasta_atividade']} | Status: {r['status']}")
