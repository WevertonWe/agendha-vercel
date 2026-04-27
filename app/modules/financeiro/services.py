import sqlite3
from typing import List, Dict, Any
from app.config import settings
from app.modules.financeiro.models import (
    FinanceiroProjetoBase, FinanceiroMetaBase, FinanceiroEtapaBase, FinanceiroRubricaBase, FinanceiroEntidadeBase, FinanceiroLancamentoBase
)

def get_db_connection():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Create Functions ---

def create_projeto(projeto: FinanceiroProjetoBase) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO financeiro_projetos (nome, numero_contrato, data_inicio, data_fim, valor_total)
            VALUES (?, ?, ?, ?, ?)
        """, (projeto.nome, projeto.numero_contrato, projeto.data_inicio, projeto.data_fim, projeto.valor_total))
        projeto_id = cursor.lastrowid
        conn.commit()
        return projeto_id

def create_meta(meta: FinanceiroMetaBase) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO financeiro_metas (projeto_id, numero_meta, descricao)
            VALUES (?, ?, ?)
        """, (meta.projeto_id, meta.numero_meta, meta.descricao))
        meta_id = cursor.lastrowid
        conn.commit()
        return meta_id

def create_etapa(etapa: FinanceiroEtapaBase) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO financeiro_etapas (meta_id, numero_etapa, descricao)
            VALUES (?, ?, ?)
        """, (etapa.meta_id, etapa.numero_etapa, etapa.descricao))
        etapa_id = cursor.lastrowid
        conn.commit()
        return etapa_id

def create_rubrica(rubrica: FinanceiroRubricaBase) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Calculate total if not provided
        if rubrica.valor_total_programado is None and rubrica.quantidade_programada and rubrica.valor_unitario_programado:
            rubrica.valor_total_programado = rubrica.quantidade_programada * rubrica.valor_unitario_programado

        cursor.execute("""
            INSERT INTO financeiro_rubricas (etapa_id, codigo, descricao, unidade, quantidade_programada, valor_unitario_programado, valor_total_programado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (rubrica.etapa_id, rubrica.codigo, rubrica.descricao, rubrica.unidade, rubrica.quantidade_programada, rubrica.valor_unitario_programado, rubrica.valor_total_programado))
        rubrica_id = cursor.lastrowid
        conn.commit()
        return rubrica_id

def create_entidade(entidade: FinanceiroEntidadeBase) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO financeiro_entidades (
                tipo_pessoa, nome_razao_social, cpf_cnpj, funcao, municipio_atuacao,
                endereco_rua, endereco_numero, endereco_bairro, endereco_cidade, endereco_cep,
                contato_telefone, contato_email, dados_bancarios_banco, dados_bancarios_agencia, dados_bancarios_conta
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entidade.tipo_pessoa, entidade.nome_razao_social, entidade.cpf_cnpj, entidade.funcao, entidade.municipio_atuacao,
            entidade.endereco_rua, entidade.endereco_numero, entidade.endereco_bairro, entidade.endereco_cidade, entidade.endereco_cep,
            entidade.contato_telefone, entidade.contato_email, entidade.dados_bancarios_banco, entidade.dados_bancarios_agencia, entidade.dados_bancarios_conta
        ))
        entidade_id = cursor.lastrowid
        conn.commit()
        return entidade_id

def create_lancamento(lancamento: FinanceiroLancamentoBase) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO financeiro_lancamentos (
                projeto_id, rubrica_id, entidade_id, data_lancamento,
                numero_processo, numero_nota_fiscal, historico,
                quantidade_executada, valor_total_executado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lancamento.projeto_id, lancamento.rubrica_id, lancamento.entidade_id, lancamento.data_lancamento,
            lancamento.numero_processo, lancamento.numero_nota_fiscal, lancamento.historico,
            lancamento.quantidade_executada, lancamento.valor_total_executado
        ))
        lancamento_id = cursor.lastrowid
        conn.commit()
        return lancamento_id

# --- Get Functions ---

def get_projeto_completo(projeto_id: int) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Get Projeto
        cursor.execute("SELECT * FROM financeiro_projetos WHERE id = ?", (projeto_id,))
        projeto_row = cursor.fetchone()
        if not projeto_row:
            return None
        
        projeto = dict(projeto_row)
        projeto['metas'] = []

        # 2. Get Metas
        cursor.execute("SELECT * FROM financeiro_metas WHERE projeto_id = ?", (projeto_id,))
        metas_rows = cursor.fetchall()

        for meta_row in metas_rows:
            meta = dict(meta_row)
            meta['etapas'] = []

            # 3. Get Etapas for each Meta
            cursor.execute("SELECT * FROM financeiro_etapas WHERE meta_id = ?", (meta['id'],))
            etapas_rows = cursor.fetchall()

            for etapa_row in etapas_rows:
                etapa = dict(etapa_row)
                etapa['rubricas'] = []

                # 4. Get Rubricas for each Etapa
                cursor.execute("SELECT * FROM financeiro_rubricas WHERE etapa_id = ?", (etapa['id'],))
                rubricas_rows = cursor.fetchall()
                
                for rubrica_row in rubricas_rows:
                    rubrica = dict(rubrica_row)
                    
                    # 5. Calculate Executed Value and Balance
                    cursor.execute("""
                        SELECT COALESCE(SUM(valor_total_executado), 0) 
                        FROM financeiro_lancamentos 
                        WHERE rubrica_id = ?
                    """, (rubrica['id'],))
                    valor_executado = cursor.fetchone()[0]
                    
                    rubrica['valor_executado'] = valor_executado
                    rubrica['saldo'] = (rubrica['valor_total_programado'] or 0) - valor_executado
                    
                    etapa['rubricas'].append(rubrica)
                
                meta['etapas'].append(etapa)
            
            projeto['metas'].append(meta)

        return projeto

def list_entidades(limit: int = 5) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM financeiro_entidades ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_all_entidades() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_razao_social FROM financeiro_entidades ORDER BY nome_razao_social")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_rubricas_flat(projeto_id: int) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                r.id, 
                r.codigo, 
                r.descricao as rubrica_descricao,
                e.numero_etapa,
                e.descricao as etapa_descricao,
                m.numero_meta,
                m.descricao as meta_descricao
            FROM financeiro_rubricas r
            JOIN financeiro_etapas e ON r.etapa_id = e.id
            JOIN financeiro_metas m ON e.meta_id = m.id
            WHERE m.projeto_id = ?
            ORDER BY r.codigo
        """, (projeto_id,))
        rows = cursor.fetchall()
        
        rubricas_flat = []
        for row in rows:
            d = dict(row)
            full_name = f"Meta {d['numero_meta']} > Etapa {d['numero_etapa']} > {d['codigo']} - {d['rubrica_descricao']}"
            rubricas_flat.append({
                "id": d['id'],
                "full_name": full_name
            })
        return rubricas_flat

def list_lancamentos(limit: int = 5) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                l.*,
                e.nome_razao_social,
                r.descricao as rubrica_descricao
            FROM financeiro_lancamentos l
            LEFT JOIN financeiro_entidades e ON l.entidade_id = e.id
            LEFT JOIN financeiro_rubricas r ON l.rubrica_id = r.id
            ORDER BY l.id DESC LIMIT ?
            """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_lancamento(lancamento_id: int) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                l.*,
                e.nome_razao_social,
                e.cpf_cnpj,
                r.descricao as rubrica_descricao,
                r.codigo as rubrica_codigo,
                p.nome as projeto_nome,
                p.numero_contrato
            FROM financeiro_lancamentos l
            LEFT JOIN financeiro_entidades e ON l.entidade_id = e.id
            LEFT JOIN financeiro_rubricas r ON l.rubrica_id = r.id
            LEFT JOIN financeiro_projetos p ON l.projeto_id = p.id
            WHERE l.id = ?
        """, (lancamento_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_dashboard_data() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Get all projects
        cursor.execute("SELECT * FROM financeiro_projetos ORDER BY id DESC")
        projetos_rows = cursor.fetchall()
        
        dashboard_data = []
        
        for row in projetos_rows:
            projeto = dict(row)
            projeto_id = projeto['id']
            
            # 2. Calculate Total Orcado (Sum of all rubricas)
            cursor.execute("""
                SELECT COALESCE(SUM(valor_total_programado), 0)
                FROM financeiro_rubricas r
                JOIN financeiro_etapas e ON r.etapa_id = e.id
                JOIN financeiro_metas m ON e.meta_id = m.id
                WHERE m.projeto_id = ?
            """, (projeto_id,))
            total_orcado = cursor.fetchone()[0]
            
            # 3. Calculate Total Executado (Sum of all lancamentos)
            cursor.execute("""
                SELECT COALESCE(SUM(valor_total_executado), 0)
                FROM financeiro_lancamentos
                WHERE projeto_id = ?
            """, (projeto_id,))
            total_executado = cursor.fetchone()[0]
            
            # 4. Calculate Saldo and Percentage
            saldo = total_orcado - total_executado
            percentual_concluido = 0
            if total_orcado > 0:
                percentual_concluido = (total_executado / total_orcado) * 100
                
            projeto['total_orcado'] = total_orcado
            projeto['total_executado'] = total_executado
            projeto['saldo'] = saldo
            projeto['percentual_concluido'] = round(percentual_concluido, 2)
            
            dashboard_data.append(projeto)
            
        return dashboard_data

def get_extrato_projeto(projeto_id: int) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                l.*,
                e.nome_razao_social,
                r.codigo as rubrica_codigo,
                r.descricao as rubrica_descricao
            FROM financeiro_lancamentos l
            LEFT JOIN financeiro_entidades e ON l.entidade_id = e.id
            LEFT JOIN financeiro_rubricas r ON l.rubrica_id = r.id
            WHERE l.projeto_id = ?
            ORDER BY l.data_lancamento DESC
        """, (projeto_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def update_projeto(projeto_id: int, data: Dict[str, Any]) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE financeiro_projetos SET
                nome = ?, numero_contrato = ?, data_inicio = ?, data_fim = ?, valor_total = ?
            WHERE id = ?
        """, (
            data.get('nome'), data.get('numero_contrato'), data.get('data_inicio'), 
            data.get('data_fim'), data.get('valor_total'), projeto_id
        ))
        conn.commit()
        return cursor.rowcount > 0

def delete_projeto(projeto_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Delete related data (cascade manually if foreign keys don't handle it)
        # 1. Delete Lancamentos
        cursor.execute("DELETE FROM financeiro_lancamentos WHERE projeto_id = ?", (projeto_id,))
        
        # 2. Delete Rubricas (via Etapas -> Metas) - This is complex to do in one query without cascade.
        # Let's rely on manual deletion or assume simple structure for now.
        # Ideally we should select all metas, then steps, then rubricas.
        
        # Get Metas
        cursor.execute("SELECT id FROM financeiro_metas WHERE projeto_id = ?", (projeto_id,))
        metas = cursor.fetchall()
        for meta in metas:
            cursor.execute("SELECT id FROM financeiro_etapas WHERE meta_id = ?", (meta['id'],))
            etapas = cursor.fetchall()
            for etapa in etapas:
                cursor.execute("DELETE FROM financeiro_rubricas WHERE etapa_id = ?", (etapa['id'],))
            cursor.execute("DELETE FROM financeiro_etapas WHERE meta_id = ?", (meta['id'],))
            
        cursor.execute("DELETE FROM financeiro_metas WHERE projeto_id = ?", (projeto_id,))
        cursor.execute("DELETE FROM financeiro_projetos WHERE id = ?", (projeto_id,))
        
        conn.commit()
        return cursor.rowcount > 0

# --- Update/Delete Functions ---

def get_entidade(entidade_id: int) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM financeiro_entidades WHERE id = ?", (entidade_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_entidade(entidade_id: int, data: Dict[str, Any]) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE financeiro_entidades SET
                tipo_pessoa = ?, nome_razao_social = ?, cpf_cnpj = ?, funcao = ?, municipio_atuacao = ?,
                endereco_rua = ?, endereco_numero = ?, endereco_bairro = ?, endereco_cidade = ?, endereco_cep = ?,
                contato_telefone = ?, contato_email = ?, dados_bancarios_banco = ?, dados_bancarios_agencia = ?, dados_bancarios_conta = ?
            WHERE id = ?
        """, (
            data.get('tipo_pessoa'), data.get('nome_razao_social'), data.get('cpf_cnpj'), data.get('funcao'), data.get('municipio_atuacao'),
            data.get('endereco_rua'), data.get('endereco_numero'), data.get('endereco_bairro'), data.get('endereco_cidade'), data.get('endereco_cep'),
            data.get('contato_telefone'), data.get('contato_email'), data.get('dados_bancarios_banco'), data.get('dados_bancarios_agencia'), data.get('dados_bancarios_conta'),
            entidade_id
        ))
        conn.commit()
        return cursor.rowcount > 0

def delete_entidade(entidade_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM financeiro_entidades WHERE id = ?", (entidade_id,))
        conn.commit()
        return cursor.rowcount > 0

def update_lancamento(lancamento_id: int, data: Dict[str, Any]) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE financeiro_lancamentos SET
                projeto_id = ?, rubrica_id = ?, entidade_id = ?, data_lancamento = ?,
                numero_processo = ?, numero_nota_fiscal = ?, historico = ?,
                quantidade_executada = ?, valor_total_executado = ?
            WHERE id = ?
        """, (
            data.get('projeto_id'), data.get('rubrica_id'), data.get('entidade_id'), data.get('data_lancamento'),
            data.get('numero_processo'), data.get('numero_nota_fiscal'), data.get('historico'),
            data.get('quantidade_executada'), data.get('valor_total_executado'),
            lancamento_id
        ))
        conn.commit()
        return cursor.rowcount > 0

def delete_lancamento(lancamento_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM financeiro_lancamentos WHERE id = ?", (lancamento_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_rubrica(rubrica_id: int) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM financeiro_rubricas WHERE id = ?", (rubrica_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_rubrica(rubrica_id: int, data: Dict[str, Any]) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Calculate total if needed
        if 'quantidade_programada' in data and 'valor_unitario_programado' in data:
             data['valor_total_programado'] = data['quantidade_programada'] * data['valor_unitario_programado']

        cursor.execute("""
            UPDATE financeiro_rubricas SET
                codigo = ?, descricao = ?, unidade = ?, quantidade_programada = ?,
                valor_unitario_programado = ?, valor_total_programado = ?
            WHERE id = ?
        """, (
            data.get('codigo'), data.get('descricao'), data.get('unidade'),
            data.get('quantidade_programada'), data.get('valor_unitario_programado'), data.get('valor_total_programado'),
            rubrica_id
        ))
        conn.commit()
        return cursor.rowcount > 0

def delete_rubrica(rubrica_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM financeiro_rubricas WHERE id = ?", (rubrica_id,))
        conn.commit()
        return cursor.rowcount > 0
