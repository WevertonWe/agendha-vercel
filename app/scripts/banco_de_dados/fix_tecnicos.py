import sqlite3
import os

# Caminhos dos bancos de dados
DB_ATUAL = "app/agendha.db"
DB_BACKUP = "app/backup_salvador.db"

def restaurar_tecnicos():
    print("--- INICIANDO RECUPERAÇÃO CIRÚRGICA DE TÉCNICOS ---")
    
    # Verificar se os arquivos existem
    if not os.path.exists(DB_ATUAL):
        print(f"ERRO: Banco atual '{DB_ATUAL}' não encontrado.")
        return
    if not os.path.exists(DB_BACKUP):
        print(f"ERRO: Banco de backup '{DB_BACKUP}' não encontrado.")
        return

    try:
        # Conexão com Backup (Leitura)
        conn_backup = sqlite3.connect(DB_BACKUP)
        cursor_backup = conn_backup.cursor()
        
        # Conexão com Atual (Escrita)
        conn_atual = sqlite3.connect(DB_ATUAL)
        cursor_atual = conn_atual.cursor()

        # Selecionar dados do backup (apenas quem tem técnico definido)
        cursor_backup.execute("""
            SELECT id, nome_tecnico, cpf_tecnico 
            FROM beneficiarios 
            WHERE nome_tecnico IS NOT NULL AND nome_tecnico != ''
        """)
        registros_backup = cursor_backup.fetchall()
        
        total_encontrados = len(registros_backup)
        print(f"Encontrados {total_encontrados} registros com técnico no backup.")

        recuperados = 0
        
        for registro in registros_backup:
            ben_id, nome_tecnico, cpf_tecnico = registro
            
            # Verificar se o beneficiário existe no banco atual
            cursor_atual.execute("SELECT id FROM beneficiarios WHERE id = ?", (ben_id,))
            if cursor_atual.fetchone():
                # Realizar o Update Cirúrgico
                cursor_atual.execute("""
                    UPDATE beneficiarios 
                    SET nome_tecnico = ?, cpf_tecnico = ? 
                    WHERE id = ?
                """, (nome_tecnico, cpf_tecnico, ben_id))
                recuperados += 1
        
        conn_atual.commit()
        print("--- FIM DA OPERAÇÃO ---")
        print(f"Total de registros processados: {total_encontrados}")
        print(f"Total de registros recuperados/atualizados: {recuperados}")

    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
    finally:
        if 'conn_backup' in locals(): conn_backup.close()  # noqa: E701
        if 'conn_atual' in locals(): conn_atual.close()  # noqa: E701

if __name__ == "__main__":
    restaurar_tecnicos()
