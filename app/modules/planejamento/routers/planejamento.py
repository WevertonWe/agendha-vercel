import sqlite3
import logging
from datetime import timedelta, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_db_connection
from app.core.auth.dependencies import get_current_user
from app.services.utils import remover_acentos
from app.modules.planejamento.schemas import (
    CronogramaExecucaoBase, 
    CronogramaUpdate, 
    SchemaGeracao
)

router = APIRouter(tags=["Planejamento e Cronograma"])

# --- TABELA AUTOMÁTICA & MIGRAÇÃO ---
def ensure_table_exists(db: sqlite3.Connection):
    try:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cronograma_execucao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                municipio TEXT NOT NULL,
                semana_referencia TEXT NOT NULL,
                quant_cisternas INTEGER DEFAULT 0,
                meta_planejada INTEGER DEFAULT 0,
                qtd_executada INTEGER DEFAULT 0
            )
        """)
        
        # Tabela de ligação many-to-many (Atualizada)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cronograma_beneficiarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cronograma_id INTEGER NOT NULL,
                beneficiario_id INTEGER NOT NULL,
                pedreiro_id INTEGER,
                data_execucao TEXT,
                FOREIGN KEY(cronograma_id) REFERENCES cronograma_execucao(id) ON DELETE CASCADE,
                FOREIGN KEY(beneficiario_id) REFERENCES beneficiarios(id) ON DELETE CASCADE
            )
        """)
        
        # Migração: Adicionar colunas novas se não existirem
        try:
            cursor.execute("SELECT pedreiro_id FROM cronograma_beneficiarios LIMIT 1")
        except sqlite3.OperationalError:
            logging.info("Migração: Adicionando colunas de execução em cronograma_beneficiarios")
            cursor.execute("ALTER TABLE cronograma_beneficiarios ADD COLUMN pedreiro_id INTEGER")
            cursor.execute("ALTER TABLE cronograma_beneficiarios ADD COLUMN data_execucao TEXT")
            
        # Migração: Coluna quant_cisternas (Legado)
        try:
            cursor.execute("SELECT quant_cisternas FROM cronograma_execucao LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE cronograma_execucao ADD COLUMN quant_cisternas INTEGER DEFAULT 0")
            
        db.commit()
    except Exception as e:
        logging.error(f"Erro ao criar/migrar tabela cronograma_execucao: {e}")

# --- ROTAS ---

@router.post("/api/planejamento/item", status_code=201)
def criar_item_planejamento(
    dados: CronogramaExecucaoBase,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    ensure_table_exists(db)
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO cronograma_execucao (municipio, semana_referencia, quant_cisternas, meta_planejada, qtd_executada)
            VALUES (?, ?, ?, ?, ?)
        """, (dados.municipio, dados.semana_referencia, dados.quant_cisternas, dados.meta_planejada, dados.qtd_executada))
        db.commit()
        return {"message": "Item criado com sucesso", "id": cursor.lastrowid}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar item: {e}")

@router.delete("/api/planejamento/item/{id}", status_code=204)
def excluir_item_planejamento(
    id: int,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM cronograma_execucao WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir item: {e}")

@router.put("/api/planejamento/item/{id}")
def atualizar_item_planejamento(
    id: int,
    dados: CronogramaUpdate,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cronograma_execucao WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    current = dict(row)
    
    # Atualiza apenas os campos enviados
    new_semana = dados.semana_referencia if dados.semana_referencia is not None else current['semana_referencia']
    new_quant = dados.quant_cisternas if dados.quant_cisternas is not None else current.get('quant_cisternas', 0)
    new_meta = dados.meta_planejada if dados.meta_planejada is not None else current['meta_planejada']
    new_exec = dados.qtd_executada if dados.qtd_executada is not None else current['qtd_executada']
    
    try:
        cursor.execute("""
            UPDATE cronograma_execucao 
            SET semana_referencia = ?, quant_cisternas = ?, meta_planejada = ?, qtd_executada = ?
            WHERE id = ?
        """, (new_semana, new_quant, new_meta, new_exec, id))
        db.commit()
        return {"message": "Item atualizado"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {e}")

@router.delete("/api/planejamento/limpar-tudo/{municipio}")
def limpar_cronograma_municipio(
    municipio: str,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM cronograma_execucao WHERE municipio = ?", (municipio,))
        db.commit()
        return {"message": "Cronograma limpo com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao limpar: {e}")

@router.post("/api/planejamento/gerar-automatico/{municipio}")
def gerar_cronograma_automatico(
    municipio: str,
    dados: SchemaGeracao,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    ensure_table_exists(db)
    cursor = db.cursor()
    
    try:
        # 1. Limpa o cronograma anterior desse município
        cursor.execute("DELETE FROM cronograma_execucao WHERE municipio = ?", (municipio,))
        
        # 2. Loop de Geração
        saldo_atual = dados.total_cisternas
        
        # Parse data string to date object
        try:
            data_atual = datetime.strptime(dados.data_inicio, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
            
        while saldo_atual > 0:
            # Se o saldo for menor que a meta (ex: sobrou 3, meta é 10), a meta vira 3.
            meta_real = min(dados.meta_semanal, saldo_atual)
            
            # Insere
            # quant_cisternas = saldo no inicio da semana
            cursor.execute("""
                INSERT INTO cronograma_execucao (municipio, semana_referencia, quant_cisternas, meta_planejada, qtd_executada)
                VALUES (?, ?, ?, ?, 0)
            """, (municipio, data_atual.strftime("%Y-%m-%d"), saldo_atual, meta_real))
            
            # Atualiza para a próxima semana
            saldo_atual -= meta_real
            data_atual += timedelta(days=7)
            
        db.commit()
        return {"message": "Cronograma gerado com sucesso!"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar cronograma: {e}")

# --- BENEFICIÁRIOS LINKING ---

@router.get("/api/planejamento/beneficiarios/busca")
def buscar_beneficiarios_para_vinculo(
    q: str,
    municipio: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    if not q or len(q) < 3:
        return []
    
    cursor = db.cursor()
    # Normalização: Retirar acentos e padronizar pra UPPERCASE (Case-insensitive via Python+DB)
    termo_limpo = f"%{remover_acentos(q).upper()}%"
    params = [termo_limpo, termo_limpo]
    
    # Obs: SQLite LIKE default é case-insensitive para ASCII, mas sem acentos a precisão sobe.
    # No SQLITE padrão, manter nome_completo cru às vezes falha pra match de acentos. 
    # Idealmente removemos no input (como feito) e dependemos de LIKE '%termo%'
    # Já que o banco SQLite não tem função Unaccent nativa padrão.
    query = """
        SELECT id, nome_completo, cpf, status, municipio
        FROM beneficiarios 
        WHERE (UPPER(nome_completo) LIKE ? OR cpf LIKE ?)
    """
    
    if municipio:
        mun_limpo = remover_acentos(municipio).upper()
        # Usa LIKE no municipio para ignorar case sem falhas de utf-8
        query += " AND UPPER(municipio) = ?"
        params.append(mun_limpo)
        
    query += " LIMIT 10"
    
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

@router.post("/api/planejamento/vincular")
def vincular_beneficiario(
    dados: dict, # { cronograma_id, beneficiario_id, pedreiro_id, data_execucao }
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    cronograma_id = dados.get('cronograma_id')
    beneficiario_id = dados.get('beneficiario_id')
    pedreiro_id = dados.get('pedreiro_id')
    data_execucao = dados.get('data_execucao')
    
    if not cronograma_id or not beneficiario_id:
        raise HTTPException(status_code=400, detail="IDs obrigatórios")
    
    ensure_table_exists(db) # Garante migração se necessário

    try:
        cursor = db.cursor()
        # Evitar duplicidade
        cursor.execute("""
            SELECT id FROM cronograma_beneficiarios 
            WHERE cronograma_id = ? AND beneficiario_id = ?
        """, (cronograma_id, beneficiario_id))
        
        if cursor.fetchone():
            return {"message": "Já vinculado"}
            
        cursor.execute("""
            INSERT INTO cronograma_beneficiarios (cronograma_id, beneficiario_id, pedreiro_id, data_execucao)
            VALUES (?, ?, ?, ?)
        """, (cronograma_id, beneficiario_id, pedreiro_id, data_execucao))
        
        # Opcional: Auto-incrementar qtd_executada
        cursor.execute("""
            UPDATE cronograma_execucao 
            SET qtd_executada = qtd_executada + 1 
            WHERE id = ?
        """, (cronograma_id,))
        
        # Atualização obrigatória na origem (Beneficiários)
        cursor.execute("""
            UPDATE beneficiarios 
            SET status = 'CONSTRUÍDA', 
                status_pagamento = 'PENDENTE', 
                pedreiro_id = ?, 
                data_conclusao = ? 
            WHERE id = ?
        """, (pedreiro_id, data_execucao, beneficiario_id))
        
        db.commit()
        return {"message": "Vínculo criado"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao vincular: {e}")

@router.delete("/api/planejamento/desvincular")
def desvincular_beneficiario(
    cronograma_id: int, 
    beneficiario_id: int,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute("""
            DELETE FROM cronograma_beneficiarios 
            WHERE cronograma_id = ? AND beneficiario_id = ?
        """, (cronograma_id, beneficiario_id))
        db.commit()
        return {"message": "Vínculo removido"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao desvincular: {e}")

# --- UPDATE GET TO INCLUDE BENEFICIARIES ---

@router.get("/api/planejamento/{municipio}")
def listar_planejamento(
    municipio: str,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    ensure_table_exists(db)
    cursor = db.cursor()
    
    # Busca itens do cronograma
    try:
        cursor.execute("""
            SELECT * FROM cronograma_execucao 
            WHERE municipio = ? 
            ORDER BY semana_referencia ASC
        """, (municipio,))
        itens = [dict(row) for row in cursor.fetchall()]

        if not itens:
            return []

        # Busca beneficiários vinculados
        ids_cronograma = [item['id'] for item in itens]
        mapa_benefs = {}
        
        if ids_cronograma:
            placeholders = ",".join("?" * len(ids_cronograma))
            # Usando doc_status que sabemos que existe no modelo/banco
            # INNER JOIN já filtra beneficiários inexistentes
            query_benefs = f"""
                SELECT cb.cronograma_id, b.id, b.nome_completo, b.status, b.doc_status
                FROM cronograma_beneficiarios cb
                JOIN beneficiarios b ON cb.beneficiario_id = b.id
                WHERE cb.cronograma_id IN ({placeholders})
            """
            cursor.execute(query_benefs, ids_cronograma)
            todos_vinculos = cursor.fetchall()
            
            for row in todos_vinculos:
                cid = row['cronograma_id']
                # Mapeia doc_status para caminho_documento para o frontend funcionar
                doc_path = row['doc_status']
                
                benef = {
                    "id": row['id'], 
                    "nome_completo": row['nome_completo'], 
                    "status": row['status'],
                    "caminho_documento": doc_path, 
                    "arquivo_caminho": doc_path 
                }
                
                if cid not in mapa_benefs:
                    mapa_benefs[cid] = []
                mapa_benefs[cid].append(benef)

        # Anexa aos itens
        for item in itens:
            item['beneficiarios'] = mapa_benefs.get(item['id'], [])
            
    except Exception as e:
        # Loga mas não trava - retorna lista vazia em último caso
        logging.error(f"Erro ao listar cronograma (Fail-safe): {e}")
        print(f"ERRO CRÍTICO NO PLANEJAMENTO: {e}")
        return []
    
    # Calcula saldos acumulados (Local para cada linha agora)
    for item in itens:
        # Garante valores numéricos
        quant = item.get('quant_cisternas') or 0
        meta = item.get('meta_planejada') or 0
        item['saldo_acumulado'] = quant - meta

    return itens
