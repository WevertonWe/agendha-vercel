import sys
import os
import logging
import sqlite3
from pathlib import Path

# Define DB_PATH directly
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "app" / "agendha.db"

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.financeiro.models import (  # noqa: E402
    FinanceiroProjetoBase, FinanceiroMetaBase, FinanceiroEtapaBase, FinanceiroRubricaBase
)

# Re-implement simple DB insertion here to avoid importing services which imports config
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_projeto(projeto: FinanceiroProjetoBase) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO financeiro_projetos (nome, numero_contrato, data_inicio, data_fim, valor_total)
        VALUES (?, ?, ?, ?, ?)
    """, (projeto.nome, projeto.numero_contrato, projeto.data_inicio, projeto.data_fim, projeto.valor_total))
    projeto_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return projeto_id

def create_meta(meta: FinanceiroMetaBase) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO financeiro_metas (projeto_id, numero_meta, descricao)
        VALUES (?, ?, ?)
    """, (meta.projeto_id, meta.numero_meta, meta.descricao))
    meta_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return meta_id

def create_etapa(etapa: FinanceiroEtapaBase) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO financeiro_etapas (meta_id, numero_etapa, descricao)
        VALUES (?, ?, ?)
    """, (etapa.meta_id, etapa.numero_etapa, etapa.descricao))
    etapa_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return etapa_id

def create_rubrica(rubrica: FinanceiroRubricaBase) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    if rubrica.valor_total_programado is None and rubrica.quantidade_programada and rubrica.valor_unitario_programado:
        rubrica.valor_total_programado = rubrica.quantidade_programada * rubrica.valor_unitario_programado

    cursor.execute("""
        INSERT INTO financeiro_rubricas (etapa_id, codigo, descricao, unidade, quantidade_programada, valor_unitario_programado, valor_total_programado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (rubrica.etapa_id, rubrica.codigo, rubrica.descricao, rubrica.unidade, rubrica.quantidade_programada, rubrica.valor_unitario_programado, rubrica.valor_total_programado))
    rubrica_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rubrica_id

def seed():
    logging.basicConfig(level=logging.INFO)
    logging.info("Iniciando seed do módulo Financeiro...")

    # 1. Create Projeto
    projeto = FinanceiroProjetoBase(
        nome="Projeto Piloto Bahia",
        numero_contrato="CTR-2023/001",
        data_inicio="2023-01-01",
        data_fim="2023-12-31",
        valor_total=100000.00
    )
    projeto_id = create_projeto(projeto)
    logging.info(f"Projeto criado com ID: {projeto_id}")

    # 2. Create Meta
    meta = FinanceiroMetaBase(
        projeto_id=projeto_id,
        numero_meta="1",
        descricao="Infraestrutura"
    )
    meta_id = create_meta(meta)
    logging.info(f"Meta criada com ID: {meta_id}")

    # 3. Create Etapa
    etapa = FinanceiroEtapaBase(
        meta_id=meta_id,
        numero_etapa="1.1",
        descricao="Obras Civis"
    )
    etapa_id = create_etapa(etapa)
    logging.info(f"Etapa criada com ID: {etapa_id}")

    # 4. Create Rubricas
    rubrica1 = FinanceiroRubricaBase(
        etapa_id=etapa_id,
        codigo="1.1.1",
        descricao="Cimento",
        unidade="Saco 50kg",
        quantidade_programada=100,
        valor_unitario_programado=35.00
    )
    rubrica1_id = create_rubrica(rubrica1)
    logging.info(f"Rubrica 'Cimento' criada com ID: {rubrica1_id}")

    rubrica2 = FinanceiroRubricaBase(
        etapa_id=etapa_id,
        codigo="1.1.2",
        descricao="Pedreiro",
        unidade="Diária",
        quantidade_programada=20,
        valor_unitario_programado=150.00
    )
    rubrica2_id = create_rubrica(rubrica2)
    logging.info(f"Rubrica 'Pedreiro' criada com ID: {rubrica2_id}")

    logging.info("Seed concluído com sucesso!")

if __name__ == "__main__":
    seed()
