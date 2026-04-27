import logging
import pandas as pd
import sqlite3
import json
from fastapi import HTTPException, UploadFile
from app.services.utils import limpar_cpf

METAS = {
    "ABARE": 159,
    "CHORROCHO": 50,
    "GLORIA": 100,
    "MACURURE": 50,
    "PAULO_AFONSO": 85,
    "RODELAS": 26
}

async def processar_conferencia_excel(arquivo_excel: UploadFile, municipio_id: str, db: sqlite3.Connection):
    """
    Lógica de negócio para verificar conferência de dados (Excel vs DB).
    Gera Lista Mestra, valida GRH e salva histórico.
    """
    logging.info(f"Iniciando verificação de conferência para município: {municipio_id}")

    # --- Passo 0: Garantir Tabela de Histórico ---
    db.execute("""
        CREATE TABLE IF NOT EXISTS historico_conferencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            municipio TEXT,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            resumo_json TEXT
        )
    """)
    db.commit()

    if not (arquivo_excel.filename.endswith('.xls') or arquivo_excel.filename.endswith('.xlsx')):
        raise HTTPException(
            status_code=400, detail="Formato de ficheiro inválido. Envie um ficheiro .xls ou .xlsx")

    try:
        # --- Passo 1: Ler o Ficheiro Excel ---
        df_excel = pd.read_excel(arquivo_excel.file, dtype=str, header=5)
        NOME_COLUNA_CPF_EXCEL = 'CPF'
        NOME_COLUNA_NOME_EXCEL = 'Nome do Beneficiário'

        if NOME_COLUNA_CPF_EXCEL not in df_excel.columns or NOME_COLUNA_NOME_EXCEL not in df_excel.columns:
            logging.error(
                f"Colunas não encontradas. Esperado: '{NOME_COLUNA_CPF_EXCEL}', '{NOME_COLUNA_NOME_EXCEL}'. Encontrado: {df_excel.columns.tolist()}")
            raise HTTPException(
                status_code=400, detail=f"Colunas não encontradas no Excel. Verifique se o ficheiro contém '{NOME_COLUNA_CPF_EXCEL}' e '{NOME_COLUNA_NOME_EXCEL}'.")

        df_excel = df_excel[[NOME_COLUNA_NOME_EXCEL,
                             NOME_COLUNA_CPF_EXCEL]].copy()
        df_excel.rename(columns={NOME_COLUNA_NOME_EXCEL: 'nome_excel',
                        NOME_COLUNA_CPF_EXCEL: 'cpf_excel'}, inplace=True)

        # --- FORÇAR STRING E DEBUG (Solicitado) ---
        # Garante que é string mesmo que o pandas tenha tentado inferir
        df_excel['cpf_excel'] = df_excel['cpf_excel'].astype(str)

        # LOG SNIPER (Rastreador Específico - Cintia)
        # Procura por CPFs que começam com 030487 para investigar a troca de final
        logging.info(">>> Iniciando Varredura Sniper para CPFs 030487... <<<")
        for idx, val in df_excel['cpf_excel'].items():
            # Limpeza manual apenas para o teste do if
            val_str = str(val).strip()
            clean_val = limpar_cpf(val)
            
            # Se o valor cru OU o limpo começar com o alvo
            if val_str.startswith("030487") or (clean_val and clean_val.startswith("030487")):
                logging.warning(f"!!! ALERTA DEBUG SNIPER [Linha {idx}] !!!")
                logging.warning(f"RAW (Excel): {val!r}")  # !r mostra aspas e caracteres ocultos
                logging.warning(f"HIGIENIZADO: {clean_val}")
                logging.warning(f"TIPO DADO:   {type(val)}")
                logging.warning("--------------------------------------------------")

        df_excel['cpf_limpo'] = df_excel['cpf_excel'].apply(limpar_cpf)

        df_excel = df_excel.dropna(subset=['cpf_limpo'])
        df_excel = df_excel.drop_duplicates(subset=['cpf_limpo'])
        logging.info(
            f"Excel lido com sucesso. Encontrados {len(df_excel)} CPFs únicos para verificar.")

        # --- Passo 2: Ler a Base de Dados Local (Filtrada por Município) ---
        
        # Mapeamento para corrigir o underscore vs espaço (Correção Solicitada)
        MAPA_MUNICIPIOS = {
            "PAULO_AFONSO": "PAULO AFONSO",
            "GRAO_MOGOL": "GRAO MOGOL"
        }
        # Se o ID estiver no mapa, usa o valor com espaço, senão usa o original
        municipio_busca = MAPA_MUNICIPIOS.get(municipio_id, municipio_id)
        logging.info(f"Buscando no banco por município: '{municipio_busca}' (Original: {municipio_id})")

        query = """
            SELECT id, cpf, cpf_familiar, cpf_tecnico, nome_completo, nome_familiar, grh
            FROM beneficiarios 
            WHERE municipio = ?
        """
        df_local = pd.read_sql_query(query, db, params=(municipio_busca,))

        df_local['cpf_limpo_1'] = df_local['cpf'].apply(limpar_cpf)
        df_local['cpf_limpo_2'] = df_local['cpf_familiar'].apply(limpar_cpf)
        df_local['cpf_limpo_3'] = df_local['cpf_tecnico'].apply(limpar_cpf)

        df_local['cpf_limpo'] = df_local['cpf_limpo_1'].fillna(
            df_local['cpf_limpo_2']).fillna(df_local['cpf_limpo_3'])

        df_local['nome_agendha'] = df_local['nome_completo'].str.strip().replace(
            '', pd.NA)
        df_local['nome_familiar_temp'] = df_local['nome_familiar'].str.strip().replace(
            '', pd.NA)
        df_local['nome_agendha'] = df_local['nome_agendha'].fillna(
            df_local['nome_familiar_temp'])

        df_local = df_local.dropna(subset=['cpf_limpo'])
        df_local = df_local.drop_duplicates(subset=['cpf_limpo'])
        df_local = df_local[['id', 'cpf_limpo', 'nome_agendha', 'grh']]

        logging.info(
            f"Base local lida com sucesso. Encontrados {len(df_local)} CPFs únicos no AGENDHA.")

        # --- Passo 3: Comparar os Dados (Merge) ---
        df_comparacao = pd.merge(
            df_excel, df_local, on='cpf_limpo', how='outer', suffixes=('_excel', '_local'))

        # --- Passo 4: Construir Lista Mestra e Estatísticas ---
        lista_mestra = []
        
        stats = {
            "total_ok": 0,
            "total_falta_gov": 0, # Está no Agendha, falta no Excel (Enviar para Gov)
            "total_falta_agendha": 0, # Está no Excel, falta no Agendha
            "total_divergentes": 0, # Nomes diferentes
            "pendentes_com_erro_grh": 0 # Falta no Gov mas não tem GRH (bloqueado)
        }

        for _, row in df_comparacao.iterrows():
            cpf = row['cpf_limpo']
            nome_excel = row.get('nome_excel')
            nome_agendha = row.get('nome_agendha')
            id_agendha = row.get('id')
            grh = row.get('grh')

            item = {
                "cpf": cpf,
                "nome_agendha": nome_agendha if pd.notna(nome_agendha) else None,
                "nome_excel": nome_excel if pd.notna(nome_excel) else None,
                "grh": grh if pd.notna(grh) else None,
                "id_agendha": int(id_agendha) if pd.notna(id_agendha) else None,
                "status": "",
                "acao_sugerida": "",
                "erro_grh": False
            }

            if pd.notna(nome_excel) and pd.notna(id_agendha):
                # Existe em ambos
                if pd.isna(nome_agendha):
                     # Caso raro: ID existe mas nome vazio
                     item["status"] = "Divergência"
                     item["acao_sugerida"] = "Corrigir Nome no Agendha"
                     stats["total_divergentes"] += 1
                elif str(nome_excel).strip().upper() == str(nome_agendha).strip().upper():
                    item["status"] = "OK"
                    item["acao_sugerida"] = "Nenhuma"
                    stats["total_ok"] += 1
                else:
                    item["status"] = "Divergência"
                    item["acao_sugerida"] = "Unificar Nomes"
                    stats["total_divergentes"] += 1
            
            elif pd.notna(id_agendha):
                # Só no Agendha (Falta enviar para o Gov)
                item["status"] = "Falta no Gov"
                item["acao_sugerida"] = "Enviar Planilha"
                stats["total_falta_gov"] += 1
                
                # Validação de GRH
                if not grh or str(grh).strip() == "":
                    item["erro_grh"] = True
                    item["acao_sugerida"] = "Preencher GRH Obrigatório"
                    stats["pendentes_com_erro_grh"] += 1
            
            elif pd.notna(nome_excel):
                # Só no Excel (Falta cadastrar no Agendha)
                item["status"] = "Falta no AGENDHA"
                item["acao_sugerida"] = "Cadastrar no Sistema"
                stats["total_falta_agendha"] += 1

            lista_mestra.append(item)

        # --- Passo 5: Metas e Histórico ---
        meta_municipio = METAS.get(municipio_id, 0)
        
        # Salvar histórico
        resumo_para_db = {
            "stats": stats,
            "meta": meta_municipio,
            "arquivo_excel": arquivo_excel.filename,
            "lista_mestra": lista_mestra  # Salvando a lista completa para permitir restauração
        }
        db.execute(
            "INSERT INTO historico_conferencias (municipio, resumo_json) VALUES (?, ?)",
            (municipio_id, json.dumps(resumo_para_db))
        )
        db.commit()

        return {
            "meta": meta_municipio,
            "estatisticas": stats,
            "lista_mestra": lista_mestra
        }

    except pd.errors.EmptyDataError:
        logging.error("O ficheiro Excel enviado está vazio.")
        raise HTTPException(
            status_code=400, detail="O ficheiro Excel enviado está vazio.")
    except Exception as e:
        logging.error(
            f"Erro ao processar o ficheiro de conferência: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail=f"Ocorreu um erro interno ao processar o ficheiro: {e}")
