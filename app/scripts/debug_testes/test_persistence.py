import os
import sqlite3
import time
import logging

# Configuração
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "agendha.db")
logging.basicConfig(level=logging.INFO, format='%(message)s')

def verificar_persistencia():
    if not os.path.exists(DB_PATH):
        logging.error(f"❌ Banco de dados não encontrado na raiz: {DB_PATH}")
        return

    # Status inicial
    stat_inicial = os.stat(DB_PATH)
    logging.info(f"📊 Status Inicial - Modificado: {time.ctime(stat_inicial.st_mtime)}, Tamanho: {stat_inicial.st_size} bytes")

    try:
        logging.info("📝 Tentando inserir registro de teste...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Cria tabela de teste se não existir
        cursor.execute("CREATE TABLE IF NOT EXISTS teste_persistencia (id INTEGER PRIMARY KEY, timestamp TEXT)")
        
        # Insere dado
        cursor.execute("INSERT INTO teste_persistencia (timestamp) VALUES (?)", (time.ctime(),))
        conn.commit()
        conn.close()
        
        logging.info("✅ Dados inseridos e commitados.")
        
        # Pequena pausa para garantir que o filesystem atualize
        time.sleep(0.1) 
        
        # Status final
        stat_final = os.stat(DB_PATH)
        logging.info(f"📊 Status Final   - Modificado: {time.ctime(stat_final.st_mtime)}, Tamanho: {stat_final.st_size} bytes")
        
        if stat_final.st_mtime > stat_inicial.st_mtime or stat_final.st_size > stat_inicial.st_size:
            logging.info("✅ SUCESSO: O arquivo do banco de dados na raiz foi alterado.")
        else:
            logging.warning("⚠️ ALERTA: O arquivo do banco de dados na raiz NÃO foi alterado. Verifique se o sistema está escrevendo em outro lugar!")

    except Exception as e:
        logging.error(f"❌ ERRO durante o teste: {e}")

if __name__ == "__main__":
    verificar_persistencia()
