import pandas as pd
import json

df_col = pd.read_csv("coletum_caracterizacao_05_2026.csv", sep=";")
migson = df_col[df_col['tecnico'].str.contains('Migson', na=False)].copy()

# Adiciona Josineide da Cruz caso esteja na pasta ou no Coletum
print(f"Total Migson em 05/2026: {len(migson)}")

registros = []
for idx, r in migson.iterrows():
    d_str = str(r['data_ativ']).split('T')[0]
    # converter para DD/MM/AAAA
    parts = d_str.split('-')
    if len(parts) == 3:
        d_format = f"{parts[2]}/{parts[1]}/{parts[0]}"
    else:
        d_format = d_str
    
    registros.append([
        "Migson Brayne Pamponet da Silva",
        str(r['beneficiario']).strip(),
        str(r['cpf']).strip(),
        str(r['comunidade']).strip(),
        str(r['municipio']).split('-')[0].strip(),
        d_format
    ])

print("Exemplo dos primeiros 3:")
print(registros[:3])

with open("migson_caracterizacao_47.json", "w", encoding="utf-8") as f:
    json.dump(registros, f, ensure_ascii=False, indent=2)
