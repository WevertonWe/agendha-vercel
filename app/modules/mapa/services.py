import sqlite3
from typing import List, Optional
from app.config import settings
from .models import PontoCreate, PontoResponse, CategoriaCreate, CategoriaResponse

def migrate_db(conn):
    cursor = conn.cursor()
    # ... (existing migrations)
    try:
        cursor.execute("SELECT endereco FROM mapa_pontos LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE mapa_pontos ADD COLUMN endereco TEXT")
        print("Migração automática: Coluna 'endereco' adicionada.")
        conn.commit()

    try:
        cursor.execute("SELECT cor FROM mapa_pontos LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE mapa_pontos ADD COLUMN cor TEXT")
        print("Migração automática: Coluna 'cor' adicionada.")
        conn.commit()
    
    try:
        cursor.execute("SELECT contexto FROM mapa_pontos LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE mapa_pontos ADD COLUMN contexto TEXT DEFAULT 'geral'")
        print("Migração automática: Coluna 'contexto' adicionada.")
        conn.commit()

    try:
        cursor.execute("SELECT responsavel FROM mapa_pontos LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE mapa_pontos ADD COLUMN responsavel TEXT")
        print("Migração automática: Coluna 'responsavel' adicionada.")
        conn.commit()

    try:
        cursor.execute("SELECT status_beneficiario FROM mapa_pontos LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE mapa_pontos ADD COLUMN status_beneficiario TEXT")
        print("Migração automática: Coluna 'status_beneficiario' adicionada.")
        conn.commit()

    try:
        cursor.execute("SELECT verificacao_bsf FROM mapa_pontos LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE mapa_pontos ADD COLUMN verificacao_bsf BOOLEAN DEFAULT 0")
        print("Migração automática: Coluna 'verificacao_bsf' adicionada.")
        conn.commit()
        
    # --- Tabela de Categorias ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mapa_categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cor TEXT NOT NULL
        )
    """)
    conn.commit()
    
    # --- Seed Default Data if Empty ---
    cursor.execute("SELECT COUNT(*) FROM mapa_categorias")
    if cursor.fetchone()[0] == 0:
        defaults = [
            ("Beneficiário", "#28a745"), # Green
            ("Cisterna", "#007bff"),      # Blue
            ("Barreiro", "#795548"),      # Brown
            ("Calçadão", "#fd7e14"),      # Orange
            ("Área de Roça", "#ffc107"),  # Yellow
            ("Área de Preservação", "#20c997"), # Teal/Greenish
            ("Outro", "#6c757d")          # Grey
        ]
        cursor.executemany("INSERT INTO mapa_categorias (nome, cor) VALUES (?, ?)", defaults)
        print("Migração automática: Categorias padrão inseridas.")
        conn.commit()

def get_db_connection():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    migrate_db(conn) # Ensure schema is up to date
    return conn

def create_ponto(ponto: PontoCreate) -> Optional[PontoResponse]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO mapa_pontos (nome, tipo, latitude, longitude, descricao, projeto_id, poligono, cor, contexto, responsavel, status_beneficiario, verificacao_bsf, endereco)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ponto.nome, ponto.tipo, ponto.latitude, ponto.longitude, ponto.descricao, ponto.projeto_id, ponto.poligono, ponto.cor, ponto.contexto, ponto.responsavel, ponto.status_beneficiario, ponto.verificacao_bsf, ponto.endereco))
        
        ponto_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return PontoResponse(id=ponto_id, **ponto.dict())
    except Exception as e:
        print(f"Erro ao criar ponto: {e}")
        return None

def get_all_pontos(contexto: str = 'geral', responsavel: Optional[str] = None) -> List[PontoResponse]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if responsavel:
            cursor.execute("SELECT * FROM mapa_pontos WHERE contexto = ? AND responsavel = ? ORDER BY id DESC", (contexto, responsavel))
        else:
            cursor.execute("SELECT * FROM mapa_pontos WHERE contexto = ? ORDER BY id DESC", (contexto,))
            
        rows = cursor.fetchall()
        conn.close()
        
        pontos = []
        for row in rows:
            # Convert sqlite3.Row to dict
            ponto_dict = dict(row)
            pontos.append(PontoResponse(**ponto_dict))
            
        return pontos
    except Exception as e:
        print(f"Erro ao buscar pontos: {e}")
        return []

def delete_ponto(ponto_id: int) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM mapa_pontos WHERE id = ?", (ponto_id,))
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    except Exception as e:
        print(f"Erro ao deletar ponto: {e}")
        return False

def get_ponto(ponto_id: int) -> Optional[PontoResponse]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM mapa_pontos WHERE id = ?", (ponto_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return PontoResponse(**dict(row))
        return None
    except Exception as e:
        print(f"Erro ao buscar ponto {ponto_id}: {e}")
        return None

def update_ponto(ponto_id: int, ponto: PontoCreate) -> Optional[PontoResponse]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE mapa_pontos 
            SET nome = ?, tipo = ?, latitude = ?, longitude = ?, descricao = ?, projeto_id = ?, poligono = ?, cor = ?, contexto = ?, status_beneficiario = ?, verificacao_bsf = ?, endereco = ?
            WHERE id = ?
        """, (ponto.nome, ponto.tipo, ponto.latitude, ponto.longitude, ponto.descricao, ponto.projeto_id, ponto.poligono, ponto.cor, ponto.contexto, ponto.status_beneficiario, ponto.verificacao_bsf, ponto.endereco, ponto_id))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            return PontoResponse(id=ponto_id, **ponto.dict())
        return None
    except Exception as e:
        print(f"Erro ao atualizar ponto {ponto_id}: {e}")
        return None

# --- Services de Categorias ---

def get_all_categorias() -> List[CategoriaResponse]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mapa_categorias ORDER BY nome ASC")
        rows = cursor.fetchall()
        conn.close()
        return [CategoriaResponse(**dict(row)) for row in rows]
    except Exception as e:
        print(f"Erro ao buscar categorias: {e}")
        return []

def create_categoria(categoria: CategoriaCreate) -> Optional[CategoriaResponse]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mapa_categorias (nome, cor) VALUES (?, ?)", (categoria.nome, categoria.cor))
        id = cursor.lastrowid
        conn.commit()
        conn.close()
        return CategoriaResponse(id=id, **categoria.dict())
    except Exception as e:
        print(f"Erro ao criar categoria: {e}")
        return None

def update_categoria(id: int, categoria: CategoriaCreate) -> Optional[CategoriaResponse]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE mapa_categorias SET nome = ?, cor = ? WHERE id = ?", (categoria.nome, categoria.cor, id))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        if rows > 0:
            return CategoriaResponse(id=id, **categoria.dict())
        return None
    except Exception as e:
        print(f"Erro ao atualizar categoria: {e}")
        return None

def delete_categoria(id: int) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mapa_categorias WHERE id = ?", (id,))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        return rows > 0
    except Exception as e:
        print(f"Erro ao deletar categoria: {e}")
        return False
