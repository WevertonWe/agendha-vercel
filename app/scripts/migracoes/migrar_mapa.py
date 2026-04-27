
import sqlite3
import os

# Caminho do banco de dados (ajustar conforme necessário)
DB_PATH = r"c:\Wev Dev\projetos\agendha\app\agendha.db"

def migrate_points():
    if not os.path.exists(DB_PATH):
        print(f"Erro: Banco de dados não encontrado em {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verificar quantos pontos estão no 'geral'
        cursor.execute("SELECT COUNT(*) FROM mapa_pontos WHERE contexto = 'geral'")
        count_geral = cursor.fetchone()[0]
        print(f"Pontos encontrados no contexto 'geral': {count_geral}")

        if count_geral > 0:
            # Atualizar todos os pontos de 'geral' para 'privado'
            cursor.execute("UPDATE mapa_pontos SET contexto = 'privado' WHERE contexto = 'geral'")
            conn.commit()
            print(f"Sucesso! {cursor.rowcount} pontos movidos de 'geral' para 'privado'.")
        else:
            print("Nenhum ponto para migrar.")

        conn.close()

    except Exception as e:
        print(f"Erro ao executar migração: {e}")

if __name__ == "__main__":
    migrate_points()
