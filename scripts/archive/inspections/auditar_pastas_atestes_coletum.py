import os
import re
from pathlib import Path
from collections import defaultdict
import pandas as pd

base_dir = Path(r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos")
ignorar = {'ATESTES', 'ATIVIDADES BAIXADAS', 'TEMP', 'UPLOADS'}

def extrair_data_mes_ano(nome):
    m = re.search(r'(\d{2})[.\/](\d{2})[.\/](\d{4})', nome)
    if m:
        return f"{m.group(2)}/{m.group(3)}", m.group(0)
    m2 = re.search(r'(\d{4})[.\/_-](\d{2})[.\/_-](\d{2})', nome)
    if m2:
        return f"{m2.group(2)}/{m2.group(1)}", f"{m2.group(3)}/{m2.group(2)}/{m2.group(1)}"
    return 'SEM_DATA', 'SEM_DATA'

dados = []

for tec_dir in base_dir.iterdir():
    if not tec_dir.is_dir() or tec_dir.name.upper() in ignorar:
        continue
    tec_nome = tec_dir.name
    doc_ativ = tec_dir / 'documentos-atividades'
    target = doc_ativ if doc_ativ.exists() else tec_dir

    for com_dir in target.iterdir():
        if not com_dir.is_dir() or 'ATIVIDADE COLETIVA' in com_dir.name.upper():
            continue
        for ben_dir in com_dir.iterdir():
            if not ben_dir.is_dir():
                continue
            
            subdirs = [s for s in ben_dir.iterdir() if s.is_dir()]
            if not subdirs:
                pdfs = list(ben_dir.glob('*.pdf'))
                if pdfs:
                    subdirs = [ben_dir]
            
            for ativ_dir in subdirs:
                pdfs = list(ativ_dir.glob('*.pdf'))
                tem_ateste = any('ATEST' in f.name.upper() for f in pdfs)
                tem_coletum = any('COL' in f.name.upper() for f in pdfs)
                
                mes_ano, data_str = extrair_data_mes_ano(ativ_dir.name)
                if mes_ano == 'SEM_DATA':
                    for f in pdfs:
                        m_a, d_s = extrair_data_mes_ano(f.name)
                        if m_a != 'SEM_DATA':
                            mes_ano, data_str = m_a, d_s
                            break

                status = 'COMPLETO'
                if tem_ateste and tem_coletum:
                    status = 'COMPLETO'
                elif tem_ateste and not tem_coletum:
                    status = 'FALTA_COLETUM'
                elif tem_coletum and not tem_ateste:
                    status = 'FALTA_ATESTE'
                else:
                    status = 'VAZIO'

                dados.append({
                    'tecnico': tec_nome,
                    'comunidade': com_dir.name,
                    'beneficiario': ben_dir.name,
                    'pasta_atividade': ativ_dir.name,
                    'data_str': data_str,
                    'mes_ano': mes_ano,
                    'status': status,
                    'tem_ateste': tem_ateste,
                    'tem_coletum': tem_coletum,
                    'total_pdfs': len(pdfs),
                    'arquivos_ateste': [f.name for f in pdfs if 'ATEST' in f.name.upper()],
                    'arquivos_coletum': [f.name for f in pdfs if 'COL' in f.name.upper()],
                    'outros_arquivos': [f.name for f in pdfs if 'ATEST' not in f.name.upper() and 'COL' not in f.name.upper()],
                    'caminho_completo': str(ativ_dir)
                })

df = pd.DataFrame(dados)
print(f"Total de pastas/atividades mapeadas: {len(df)}")
print("\n=== RESUMO GERAL POR STATUS ===")
print(df['status'].value_counts())

print("\n=== RESUMO POR MÊS/ANO E STATUS ===")
resumo_mes = df.groupby(['mes_ano', 'status']).size().unstack(fill_value=0)
print(resumo_mes)

print("\n=== DETALHE DO MÊS 08/2026 ===")
df_m08 = df[df['mes_ano'] == '08/2026']
print(f"Total no Mês 08/2026: {len(df_m08)}")
print(df_m08['status'].value_counts())
print("\nPor Técnico no Mês 08/2026:")
if not df_m08.empty:
    print(df_m08.groupby(['tecnico', 'status']).size().unstack(fill_value=0))

# Salva em CSV para consulta detalhada
df.to_csv("auditoria_pastas_ateste_coletum_geral.csv", index=False, sep=";", encoding="utf-8-sig")
df_falta_coletum = df[df['status'] == 'FALTA_COLETUM']
df_falta_coletum.to_csv("pendencias_falta_coletum.csv", index=False, sep=";", encoding="utf-8-sig")
df_falta_ateste = df[df['status'] == 'FALTA_ATESTE']
df_falta_ateste.to_csv("pendencias_falta_ateste.csv", index=False, sep=";", encoding="utf-8-sig")

print(f"\nArquivos salvos: auditoria_pastas_ateste_coletum_geral.csv, pendencias_falta_coletum.csv, pendencias_falta_ateste.csv")
