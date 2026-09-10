import pandas as pd

excel_path = r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos\ATIVIDADES BAIXADAS\visita tecnica avaliativa mes 8\formulario-de-visita-tecnica-a-v1-0-03-09-2026-09-42-18.xlsx"
df_excel = pd.read_excel(excel_path)
print(f"Colunas do Excel ({len(df_excel)} linhas):")
print(df_excel.columns.tolist()[:15])
print("\nPrimeiras 3 linhas:")
print(df_excel.iloc[:3, :8])
