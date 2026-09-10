import pandas as pd
import unicodedata
import re

def norm(text):
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', str(text))
    s = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub(r'[^A-Z0-9]', '', s.upper())

df_pend = pd.read_csv('pendencias_falta_coletum.csv', sep=';')
df_m08 = df_pend[df_pend['mes_ano'] == '08/2026'].copy()

# Coletum Excel
excel_path = r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos\ATIVIDADES BAIXADAS\visita tecnica avaliativa mes 8\formulario-de-visita-tecnica-a-v1-0-03-09-2026-09-42-18.xlsx"
df_coletum = pd.read_excel(excel_path, sheet_name="Formulario de Visita Tecnica A")

# Na planilha do Coletum, a coluna do beneficiário tem formato: 'NOME - CPF'
# Ex: 'CLAUDEJANE SOUZA OLIVEIRA FERNANDES - 859.124.615-21'
col_ben = 'Dados de Execu\u00e7\u00e3o > Benefici\u00e1rio (a): (R\u00f3tulo)'
df_coletum['nome_limpo'] = df_coletum[col_ben].astype(str).apply(lambda x: x.split('-')[0].strip())
df_coletum['nome_norm'] = df_coletum['nome_limpo'].apply(norm)

df_m08['ben_norm'] = df_m08['beneficiario'].apply(norm)

coletum_names_set = set(df_coletum['nome_norm'].tolist())

df_m08['no_coletum_excel'] = df_m08['ben_norm'].apply(lambda x: any(x in c or c in x for c in coletum_names_set))

encontrados = df_m08['no_coletum_excel'].sum()
nao_encontrados = len(df_m08) - encontrados
print(f"Total Mês 8 com Ateste aguardando Coletum: {len(df_m08)}")
print(f"Destes, encontrados no Excel do Coletum baixado: {encontrados}")
print(f"Não encontrados no Excel do Coletum baixado: {nao_encontrados}")

if nao_encontrados > 0:
    print("\nExemplos de não encontrados no Excel:")
    print(df_m08[~df_m08['no_coletum_excel']][['tecnico', 'comunidade', 'beneficiario', 'pasta_atividade']].head(10))
