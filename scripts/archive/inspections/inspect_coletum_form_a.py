import openpyxl
import pandas as pd

excel_path = r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos\ATIVIDADES BAIXADAS\visita tecnica avaliativa mes 8\formulario-de-visita-tecnica-a-v1-0-03-09-2026-09-42-18.xlsx"
df_form = pd.read_excel(excel_path, sheet_name="Formulario de Visita Tecnica A")
print(f"Total de registros na aba 'Formulario de Visita Tecnica A': {len(df_form)}")
print("Colunas:", df_form.columns.tolist()[:10])

col_data = [c for c in df_form.columns if 'Data' in c or 'data' in c]
col_tec = [c for c in df_form.columns if 'tcnico' in c or 'tecnico' in c or 'responsvel' in c or 'Nome' in c]
col_ben = [c for c in df_form.columns if 'Beneficirio' in c or 'beneficiario' in c]
col_com = [c for c in df_form.columns if 'Comunidade' in c or 'comunidade' in c]

print(f"Colunas detectadas: Data={col_data}, Tec={col_tec}, Ben={col_ben}, Com={col_com}")

if col_data:
    df_form['data_convertida'] = pd.to_datetime(df_form[col_data[0]], errors='coerce')
    print("Contagem por mês/ano no Coletum Formulario A:")
    print(df_form['data_convertida'].dt.to_period('M').value_counts())
