import pandas as pd
df = pd.read_csv('auditoria_caracterizacao_05_2026.csv', sep=';')
for idx, r in df.iterrows():
    print(f"{idx+1:02d}. ID: {r['coletum_id']} | Coletum: {r['coletum_ben']} | Pasta: {r['pasta_ben']} | Status: {r['status_pasta']} | Ratio: {r['ratio']}")
