import sqlite3
import os

db_path = r"d:\Cursos\Weverton Wilson (Projetos)\Projetos\programacao\projeto-agendha\app\agendha.db"

if not os.path.exists(db_path):
    print(f"ERRO: Banco de dados não encontrado em {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Contar total
    cursor.execute("SELECT COUNT(*) FROM beneficiarios")
    total = cursor.fetchone()[0]
    print(f"Total de beneficiários: {total}")
    
    if total > 0:
        # Verificar municipios
        cursor.execute("SELECT municipio, status, COUNT(*) FROM beneficiarios GROUP BY municipio, status LIMIT 20")
        print("\n--- Amostra de Agrupamento (Municipio, Status) ---")
        for row in cursor.fetchall():
            print(row)
            
        # Verificar se há municipios nulos/vazios
        cursor.execute("SELECT COUNT(*) FROM beneficiarios WHERE municipio IS NULL OR municipio = ''")
        sem_municipio = cursor.fetchone()[0]
        print(f"\nBeneficiários sem município: {sem_municipio}")
        
    conn.close()

except Exception as e:
    print(f"Erro ao ler banco de dados: {e}")
