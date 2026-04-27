import sqlite3
import os  # noqa: F401

DB_PATH = "agendha.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(">>> Iniciando Migração: Pivotagem BSF Atividades...")

    # 1. Criar tabela bsf_atividades
    print("1. Criando tabela bsf_atividades...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bsf_atividades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        meta_padrao INTEGER DEFAULT 0
    )
    """)

    # 2. Seed Atividades
    print("2. Populando atividades...")
    atividades = [
        ("Reunião de Articulação", "Reuniões com lideranças e parceiros"),
        ("Cadastro Familiar", "Cadastro de famílias no sistema"),
        ("Visita Técnica Social", "Visitas de acompanhamento a famílias"),
        ("Oficina de Capacitação", "Oficinas e treinamentos"),
        ("Implantação de Fomento", "Entregas e implementações"),
        ("Monitoramento", "Ações de monitoramento geral")
    ]
    
    for nome, desc in atividades:
        try:
            cursor.execute("INSERT INTO bsf_atividades (nome, descricao) VALUES (?, ?)", (nome, desc))
        except sqlite3.IntegrityError:
            pass # Já existe

    # 3. Criar tabela bsf_metas_composicao
    print("3. Criando tabela bsf_metas_composicao...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bsf_metas_composicao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meta_id INTEGER NOT NULL,
        atividade_id INTEGER NOT NULL,
        valor_meta INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(meta_id) REFERENCES bsf_metas(id) ON DELETE CASCADE,
        FOREIGN KEY(atividade_id) REFERENCES bsf_atividades(id)
    )
    """)

    # 4. Alterar tabela bsf_visitas (Adicionar atividade_id)
    print("4. Alterando bsf_visitas...")
    # Verificar se coluna já existe
    cursor.execute("PRAGMA table_info(bsf_visitas)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'atividade_id' not in columns:
        cursor.execute("ALTER TABLE bsf_visitas ADD COLUMN atividade_id INTEGER REFERENCES bsf_atividades(id)")
        print("   -> Coluna atividade_id adicionada.")
    else:
        print("   -> Coluna atividade_id já existe.")

    # 5. Migrar visitas existentes para 'Visita Técnica Social'
    print("5. Migrando dados existentes...")
    cursor.execute("SELECT id FROM bsf_atividades WHERE nome = 'Visita Técnica Social'")
    visita_tecnica_id = cursor.fetchone()
    
    if visita_tecnica_id:
        vid = visita_tecnica_id[0]
        cursor.execute("UPDATE bsf_visitas SET atividade_id = ? WHERE atividade_id IS NULL", (vid,))
        print(f"   -> {cursor.rowcount} visitas atualizadas para 'Visita Técnica Social'.")

    conn.commit()
    conn.close()
    print(">>> Migração Concluída com Sucesso! 🚀")

if __name__ == "__main__":
    migrate()
