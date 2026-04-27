
import sqlite3
import os  # noqa: F401

# Database path
DB_PATH = 'agendha.db'

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- 1. Creating/Verifying Tables ---")
    
    # Table: bsf_atividades (Ensure it exists and has correct columns)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bsf_atividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        )
    """)

    # Table: bsf_metas_contrato (New Table)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bsf_metas_contrato (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            atividade_id INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            meta_mensal INTEGER DEFAULT 0,
            meta_anual INTEGER DEFAULT 0,
            FOREIGN KEY (atividade_id) REFERENCES bsf_atividades(id),
            UNIQUE(atividade_id, ano)
        )
    """)
    
    print("Tables verified.")

    print("--- 2. Seeding Activities and Goals ---")

    # List provided by user
    # Format: (Name, Monthly Goal, Total Goal)
    data = [
        ("Reunião de Articulação com os Parceiros", 1, 6),
        ("Levantamento Socioeconômico e Geolocalização", 41, 490),
        ("Cadastro do Grupo Familiar", 41, 490),
        ("Caracterização da UPF I (Inicial)", 41, 490),
        ("Caracterização da UPF II (Intermediária)", 41, 490),
        ("Caracterização da UPF III (Final)", 41, 490),
        ("Visita Técnica Social", 163, 1960),
        ("Elaboração do Plano Produtivo da UPF", 41, 490),
        ("Visita Técnica", 898, 10771),
        ("Demonstração Didática", 25, 300),
        ("Seminário Territorial", 1, 1),
        ("Seminário Final", 1, 1),
        ("Excursão/Intercâmbio", 1, 12),
        ("Curso", 8, 93),
        ("Oficina Temática", 8, 96),
        ("Dia de Campo", 8, 96),
    ]

    for nome, meta_mensal, meta_anual in data:
        # 1. Insert/Get Activity
        cursor.execute("SELECT id FROM bsf_atividades WHERE nome = ?", (nome,))
        row = cursor.fetchone()
        
        if row:
            atividade_id = row[0]
            # Update desc if needed? No, just keep ID.
        else:
            print(f"Creating activity: {nome}")
            cursor.execute("INSERT INTO bsf_atividades (nome) VALUES (?)", (nome,))
            atividade_id = cursor.lastrowid

        # 2. Insert/Update Contract Goal for 2026 (assuming current contract year)
        # Also doing for 2025 just in case, or just 2026? The user didn't specify year, but request mentions "Contrato 014/2024". 
        # Usually projects span years. I will insert for 2025 and 2026 to be safe or just 2026 based on previous context "2026/2025" filters.
        # Let's assume 2026 as primary active year based on HTML.
        
        anos = [2025, 2026]
        for ano in anos:
            cursor.execute("SELECT id FROM bsf_metas_contrato WHERE atividade_id = ? AND ano = ?", (atividade_id, ano))
            goal_row = cursor.fetchone()
            
            if goal_row:
                # Update
                cursor.execute("""
                    UPDATE bsf_metas_contrato 
                    SET meta_mensal = ?, meta_anual = ? 
                    WHERE id = ?
                """, (meta_mensal, meta_anual, goal_row[0]))
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO bsf_metas_contrato (atividade_id, ano, meta_mensal, meta_anual)
                    VALUES (?, ?, ?, ?)
                """, (atividade_id, ano, meta_mensal, meta_anual))

    conn.commit()
    print("Seeding completed successfully.")
    conn.close()

if __name__ == "__main__":
    seed_database()
