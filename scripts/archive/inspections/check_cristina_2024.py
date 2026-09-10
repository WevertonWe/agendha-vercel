import os
import time
from pathlib import Path
import pandas as pd
import fitz

df = pd.read_csv('pendencias_falta_coletum.csv', sep=';')
c_2024 = df[df['mes_ano'] == '08/2024']
print(f"Total em 08/2024: {len(c_2024)}")
for idx, row in c_2024.iterrows():
    p = Path(row['caminho_completo'])
    pdfs = list(p.glob('*.pdf'))
    for pdf in pdfs:
        t_str = time.strftime('%d/%m/%Y %H:%M', time.localtime(pdf.stat().st_mtime))
        # ler texto do pdf para ver se tem data impressa
        txt = ""
        try:
            doc = fitz.open(pdf)
            txt = doc[0].get_text()[:300]
            doc.close()
        except:
            pass
        print(f"Beneficiário: {row['beneficiario']} | Pasta: {row['pasta_atividade']} | Modif: {t_str}")
