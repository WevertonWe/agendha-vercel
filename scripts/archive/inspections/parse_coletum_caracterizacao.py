import asyncio
import pandas as pd
from app.services.coletum_service import buscar_respostas_formulario

async def main():
    print("Baixando todas as 482 respostas de Caracterização I (Formulário 37205)...")
    respostas = await buscar_respostas_formulario("37205", limit=2000)
    
    lista = []
    for r in respostas:
        ans_id = r.get('id')
        ans = r.get('answer', {})
        
        # Procura grupo dados_de_execucao
        exec_dados = {}
        for k, v in ans.items():
            if 'dados_de_execucao' in k and isinstance(v, dict):
                exec_dados = v
                break
        
        # Procura grupo dados_do_grupo_familiar
        fam_dados = {}
        for k, v in ans.items():
            if ('grupo_familiar' in k or 'beneficiario' in k) and isinstance(v, dict):
                fam_dados = v
                break
        
        # Procura campos de técnico, data, comunidade, beneficiário, cpf
        tecnico = None
        data_ativ = None
        comunidade = None
        municipio = None
        beneficiario = None
        cpf = None
        
        for k, v in exec_dados.items():
            if 'tecnico' in k and 'nome' in k:
                tecnico = v
            elif 'data' in k:
                data_ativ = v
            elif 'comunidade' in k:
                comunidade = v
            elif 'municipio' in k:
                municipio = v
            elif 'beneficiario' in k and not beneficiario:
                beneficiario = v
            elif 'cpf' in k and 'tecnico' not in k:
                cpf = v
        
        for k, v in fam_dados.items():
            if 'nome' in k:
                beneficiario = v
            elif 'cpf' in k:
                cpf = v

        # Se ainda não achou beneficiário, varre tudo em ans
        if not beneficiario:
            for k, sub in ans.items():
                if isinstance(sub, dict):
                    for sk, sv in sub.items():
                        if 'beneficiario' in sk or ('nome' in sk and 'tecnico' not in sk):
                            beneficiario = sv
                        if 'cpf' in sk and 'tecnico' not in sk:
                            cpf = sv

        lista.append({
            'answer_id': ans_id,
            'tecnico': tecnico,
            'comunidade': comunidade,
            'municipio': municipio,
            'beneficiario': beneficiario,
            'cpf': cpf,
            'data_ativ': str(data_ativ),
        })

    df_col = pd.DataFrame(lista)
    print(f"Total processado: {len(df_col)}")
    df_col['mes_ano'] = df_col['data_ativ'].apply(lambda d: f"{d.split('-')[1]}/{d.split('-')[0]}" if len(d.split('-')) >= 2 and len(d.split('-')[0]) == 4 else 'SEM_DATA')
    
    print("\nRespostas de Caracterização I por Mês/Ano no Coletum:")
    print(df_col['mes_ano'].value_counts())
    
    df_col.to_csv("coletum_caracterizacao_todas.csv", index=False, sep=";", encoding="utf-8-sig")
    
    m05 = df_col[df_col['mes_ano'] == '05/2026']
    print(f"\nTotal no Coletum em 05/2026: {len(m05)}")
    print("\nPor Técnico no Coletum em 05/2026:")
    print(m05['tecnico'].value_counts())
    m05.to_csv("coletum_caracterizacao_05_2026.csv", index=False, sep=";", encoding="utf-8-sig")

asyncio.run(main())
