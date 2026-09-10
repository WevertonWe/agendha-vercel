import os
import re
from pathlib import Path
from collections import defaultdict
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

base_dir = Path(r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos")
ignorar = {'ATESTES', 'ATIVIDADES BAIXADAS', 'TEMP', 'UPLOADS'}

def extrair_data_mes_ano(nome):
    m = re.search(r'(\d{2})[.\/](\d{2})[.\/](\d{4})', nome)
    if m:
        dia, mes, ano = m.group(1), m.group(2), m.group(3)
        return f"{mes}/{ano}", f"{dia}/{mes}/{ano}", dia, mes, ano
    m2 = re.search(r'(\d{4})[.\/_-](\d{2})[.\/_-](\d{2})', nome)
    if m2:
        ano, mes, dia = m2.group(1), m2.group(2), m2.group(3)
        return f"{mes}/{ano}", f"{dia}/{mes}/{ano}", dia, mes, ano
    return 'SEM_DATA', 'SEM_DATA', '', '', ''

def extrair_tipo_atividade(nome):
    n = nome.upper()
    if 'AVALIATIVA' in n:
        return 'VISITA TÉCNICA AVALIATIVA'
    if 'PLANO PRODUTIVO' in n or 'PLANO' in n:
        return 'PLANO PRODUTIVO'
    if 'SOCIO' in n or 'GEOLOCALIZACAO' in n:
        return 'LEVANTAMENTO SOCIOECONÔMICO'
    if 'CARACTERIZACAO' in n or 'UPF' in n:
        return 'CARACTERIZAÇÃO'
    if 'VISITA' in n:
        return 'VISITA TÉCNICA'
    if 'OFICINA' in n:
        return 'OFICINA TEMÁTICA'
    return 'OUTROS'

registros = []

for tec_dir in sorted(base_dir.iterdir()):
    if not tec_dir.is_dir() or tec_dir.name.upper() in ignorar:
        continue
    tec_nome = tec_dir.name
    doc_ativ = tec_dir / 'documentos-atividades'
    target = doc_ativ if doc_ativ.exists() else tec_dir

    for com_dir in sorted(target.iterdir()):
        if not com_dir.is_dir() or 'ATIVIDADE COLETIVA' in com_dir.name.upper():
            continue
        for ben_dir in sorted(com_dir.iterdir()):
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
                
                mes_ano, data_str, dia, mes, ano = extrair_data_mes_ano(ativ_dir.name)
                if mes_ano == 'SEM_DATA':
                    for f in pdfs:
                        m_a, d_s, d, m, a = extrair_data_mes_ano(f.name)
                        if m_a != 'SEM_DATA':
                            mes_ano, data_str, dia, mes, ano = m_a, d_s, d, m, a
                            break

                # Detecção inteligente de erros de digitação:
                # 1. Pastas com '08/2024' modificadas recentemente (em 08/09/2026) são na verdade 08/2026
                alerta_ano = None
                if mes_ano == '08/2024' and tec_nome == 'cristina':
                    mes_ano_ajustado = '08/2026'
                    alerta_ano = 'Ano 2024 na pasta (Ateste escaneado em 08/09/2026 - Na verdade é 08/2026)'
                elif '2500' in mes_ano:
                    mes_ano_ajustado = mes_ano.replace('2500', '2025')
                    alerta_ano = f'Ano 2500 na pasta (Erro de digitação - Na verdade é {mes_ano_ajustado})'
                elif mes_ano == '11/2026':
                    mes_ano_ajustado = '11/2025'
                    alerta_ano = 'Ano 2026 futuro na pasta (Na verdade é 11/2025)'
                elif mes_ano == '08/2020':
                    mes_ano_ajustado = '08/2025'
                    alerta_ano = 'Ano 2020 na pasta (Possível 08/2025)'
                else:
                    mes_ano_ajustado = mes_ano

                status = 'COMPLETO'
                if tem_ateste and tem_coletum:
                    status = 'COMPLETO'
                elif tem_ateste and not tem_coletum:
                    status = 'FALTA_COLETUM'
                elif tem_coletum and not tem_ateste:
                    status = 'FALTA_ATESTE'
                else:
                    status = 'VAZIO'

                tipo_ativ = extrair_tipo_atividade(ativ_dir.name)

                registros.append({
                    'tecnico': tec_nome,
                    'comunidade': com_dir.name,
                    'beneficiario': ben_dir.name,
                    'pasta_atividade': ativ_dir.name,
                    'tipo_atividade': tipo_ativ,
                    'data_atividade': data_str,
                    'mes_ano': mes_ano_ajustado,
                    'mes_ano_original': mes_ano,
                    'alerta_ano': alerta_ano or '',
                    'ano': ano,
                    'mes': mes,
                    'status': status,
                    'tem_ateste': 'SIM' if tem_ateste else 'NÃO',
                    'tem_coletum': 'SIM' if tem_coletum else 'NÃO',
                    'arquivos_ateste': ", ".join([f.name for f in pdfs if 'ATEST' in f.name.upper()]),
                    'arquivos_coletum': ", ".join([f.name for f in pdfs if 'COL' in f.name.upper()]),
                    'outros_arquivos': ", ".join([f.name for f in pdfs if 'ATEST' not in f.name.upper() and 'COL' not in f.name.upper()]),
                    'caminho_pasta': str(ativ_dir)
                })

df = pd.DataFrame(registros)

# Criar Relatório Excel Formatado
relatorio_path = "Relatorio_Auditoria_Ateste_Coletum_Pastas.xlsx"
wb = openpyxl.Workbook()
wb.remove(wb.active) # Remove default sheet

header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_fill_blue = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
header_fill_orange = PatternFill(start_color="C65911", end_color="C65911", fill_type="solid")
header_fill_red = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
header_fill_green = PatternFill(start_color="385723", end_color="385723", fill_type="solid")
thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

def formatar_aba(ws, header_fill):
    ws.views.sheetView[0].showGridLines = True
    for col_idx, col in enumerate(ws.iter_cols(min_row=1, max_row=ws.max_row), start=1):
        # Header formatting
        header_cell = ws.cell(1, col_idx)
        header_cell.font = header_font
        header_cell.fill = header_fill
        header_cell.alignment = Alignment(horizontal="center", vertical="center")
        
        max_len = len(str(header_cell.value or ''))
        for cell in col[1:]:
            cell.border = thin_border
            val_str = str(cell.value or '')
            if len(val_str) > max_len:
                max_len = len(val_str)
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = min(max_len + 4, 50)
    ws.row_dimensions[1].height = 25

# ABA 1: RESUMO EXECUTIVO
ws1 = wb.create_sheet(title="Resumo Geral")
ws1.append(["Mês/Ano", "Total Atividades", "Completas (Ateste+Coletum)", "Falta Coletum (Tem Ateste)", "Falta Ateste (Tem Coletum)", "Pastas Vazias", "% Conformidade"])

resumo_mes = df.groupby('mes_ano').agg(
    total=('status', 'count'),
    completas=('status', lambda s: (s == 'COMPLETO').sum()),
    falta_coletum=('status', lambda s: (s == 'FALTA_COLETUM').sum()),
    falta_ateste=('status', lambda s: (s == 'FALTA_ATESTE').sum()),
    vazias=('status', lambda s: (s == 'VAZIO').sum())
).reset_index()

resumo_mes['pct_conformidade'] = ((resumo_mes['completas'] / resumo_mes['total']) * 100).round(1).astype(str) + '%'

# Ordenar resumo
for _, row in resumo_mes.sort_values(by='mes_ano').iterrows():
    ws1.append([row['mes_ano'], row['total'], row['completas'], row['falta_coletum'], row['falta_ateste'], row['vazias'], row['pct_conformidade']])

formatar_aba(ws1, header_fill_blue)

# ABA 2: MÊS 08/2026 - FALTA COLETUM (PRIORIDADE IMEDIATA)
ws2 = wb.create_sheet(title="Mês 8 - Baixar Coletum")
ws2.append(["Técnico", "Comunidade", "Beneficiário", "Tipo Atividade", "Data Atividade", "Pasta da Atividade", "Ateste Escaneado (Já na pasta)", "Status", "Observações / Alerta"])

df_m08_fc = df[(df['mes_ano'] == '08/2026') & (df['status'] == 'FALTA_COLETUM')].sort_values(by=['tecnico', 'comunidade', 'beneficiario'])
for _, row in df_m08_fc.iterrows():
    ws2.append([
        row['tecnico'], row['comunidade'], row['beneficiario'], row['tipo_atividade'],
        row['data_atividade'], row['pasta_atividade'], row['arquivos_ateste'], "PRECISA BAIXAR COLETUM", row['alerta_ano']
    ])
formatar_aba(ws2, header_fill_orange)

# ABA 3: OUTROS MESES - FALTA COLETUM
ws3 = wb.create_sheet(title="Outros Meses - Falta Coletum")
ws3.append(["Mês/Ano", "Técnico", "Comunidade", "Beneficiário", "Tipo Atividade", "Data Atividade", "Pasta da Atividade", "Ateste Escaneado", "Status", "Observações / Alerta"])

df_outros_fc = df[(df['mes_ano'] != '08/2026') & (df['status'] == 'FALTA_COLETUM')].sort_values(by=['mes_ano', 'tecnico', 'beneficiario'])
for _, row in df_outros_fc.iterrows():
    ws3.append([
        row['mes_ano'], row['tecnico'], row['comunidade'], row['beneficiario'], row['tipo_atividade'],
        row['data_atividade'], row['pasta_atividade'], row['arquivos_ateste'], "PRECISA BAIXAR COLETUM", row['alerta_ano']
    ])
formatar_aba(ws3, header_fill_orange)

# ABA 4: FALTA ATESTE (TODOS OS MESES)
ws4 = wb.create_sheet(title="Todas - Falta Ateste")
ws4.append(["Mês/Ano", "Técnico", "Comunidade", "Beneficiário", "Tipo Atividade", "Data Atividade", "Pasta da Atividade", "Coletum Existente", "Status"])

df_fa = df[df['status'] == 'FALTA_ATESTE'].sort_values(by=['mes_ano', 'tecnico', 'beneficiario'])
for _, row in df_fa.iterrows():
    ws4.append([
        row['mes_ano'], row['tecnico'], row['comunidade'], row['beneficiario'], row['tipo_atividade'],
        row['data_atividade'], row['pasta_atividade'], row['arquivos_coletum'], "PRECISA ESCANEAR ATESTE"
    ])
formatar_aba(ws4, header_fill_red)

# ABA 5: ANOS ATÍPICOS / VAZIOS
ws5 = wb.create_sheet(title="Alertas Pastas Atípicas")
ws5.append(["Tipo de Alerta", "Técnico", "Comunidade", "Beneficiário", "Pasta da Atividade", "Arquivos Encontrados", "Caminho Completo"])

for _, row in df.iterrows():
    alerta = row['alerta_ano']
    if not alerta and row['status'] == 'VAZIO':
        alerta = "Pasta Vazia sem PDFs"
    
    if alerta:
        arq = row['arquivos_ateste'] or row['arquivos_coletum'] or row['outros_arquivos'] or 'Nenhum'
        ws5.append([alerta, row['tecnico'], row['comunidade'], row['beneficiario'], row['pasta_atividade'], arq, row['caminho_pasta']])

formatar_aba(ws5, header_fill_red)

wb.save(relatorio_path)
print("Relatorio Excel atualizado com sucesso:", relatorio_path)
print("Total Mes 8 aguardando Coletum:", len(df_m08_fc))
print("Total Outros Meses aguardando Coletum:", len(df_outros_fc))
print("Total aguardando Ateste:", len(df_fa))

