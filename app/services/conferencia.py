import logging
# import pandas as pd
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
        raise HTTPException(status_code=501, detail="Conferência de Excel desativada na versão Cloud para economia de RAM.")
    except Exception as e:
        logging.error(f"Erro ao processar: {e}")
        raise e
