import sqlite3
import os
import sys

# --- CONFIGURAÇÃO ---
TARGET_COUNT = 44
OUTPUT_FILE = "relatorio_gloria_kantarure.txt"

def find_valid_db():
    """Tenta localizar um banco de dados que contenha a tabela 'beneficiarios'."""
    candidates = [
        "agendha.db",      # Tentar raiz primeiro (muitas vezes é o real em dev)
        "app/agendha.db",  
        "backups/agendha.db.bak"
    ]
    
    print("🔍 Procurando bancos de dados candidatos...")
    
    for candidate in candidates:
        if os.path.exists(candidate):
            print(f"   ➡ Verificando: {candidate} ... ", end="")
            try:
                conn = sqlite3.connect(candidate)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='beneficiarios'")
                if cursor.fetchone():
                    print("✅ Tabela encontrada!")
                    conn.close()
                    return candidate
                else:
                    print("❌ Tabela 'beneficiarios' ausente.")
                    conn.close()
            except Exception as e:
                print(f"❌ Erro ao abrir: {e}")
                
    return None

def extract():
    db_path = find_valid_db()
    
    if not db_path:
        print("❌ ERRO FATAL: Nenhum banco de dados com a tabela 'beneficiarios' foi encontrado.")
        sys.exit(1)

    print(f"\n📂 Usando banco de dados: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 2. Executar Query
        print(f"📊 Executando filtro: Município='GLORIA', Comunidade='Kantarure'")  # noqa: F541
        query = """
        SELECT nome_familiar, cpf_familiar 
        FROM beneficiarios 
        WHERE UPPER(municipio) = 'GLORIA' 
        AND comunidade LIKE '%Kantarure%'
        ORDER BY nome_familiar ASC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        count = len(rows)
        print(f"📈 Registros encontrados: {count}")
        
        if count == 0:
            print("⚠️ AVISO: Nenhum registro encontrado. Verificando amostra de dados...")
            cursor.execute("SELECT DISTINCT municipio, comunidade FROM beneficiarios LIMIT 10")
            print("Amostra de locais:", cursor.fetchall())
        
        # 3. Gerar Arquivo
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"RELATÓRIO DE BENEFICIÁRIOS - GLORIA / KANTARURE\n")  # noqa: F541
            f.write(f"Data de Geração: {os.path.basename(db_path)}\n")
            f.write(f"Total Encontrado: {count}\n")
            f.write("="*70 + "\n")
            f.write(f"{'NOME FAMILIAR':<50} | {'CPF'}\n")
            f.write("-" * 70 + "\n")
            
            for row in rows:
                nome = row[0] or "NÃO INFORMADO"
                cpf = row[1] or "---"
                f.write(f"{nome:<50} | {cpf}\n")
            
            f.write("-" * 70 + "\n")
            f.write("FIM DO RELATÓRIO\n")
        
        print(f"✅ Arquivo gerado com sucesso: {os.path.abspath(OUTPUT_FILE)}")
        
        # Validação final
        if count == TARGET_COUNT:
            print("✨ SUCESSO TOTAL: Contagem exata (44) confirmada.")
        elif count > 0:
            print(f"⚠️ ATENÇÃO: Contagem divergente da meta ({count} vs {TARGET_COUNT}). Verifique o arquivo.")
            
    except sqlite3.Error as e:
        print(f"❌ Erro de Banco de Dados: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro Inesperado: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    extract()
