import os
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    # Carregar .env em ambiente de desenvolvimento local se as variáveis não estiverem setadas
    if not os.getenv("SUPABASE_DB_STRING"):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

    db_string = os.getenv("SUPABASE_DB_STRING")
    if not db_string:
        logger.error("CRITICAL: SUPABASE_DB_STRING is not set in environment or .env!")
        exit(1)

    logger.info("Connecting to Supabase Database...")
    try:
        conn = psycopg2.connect(db_string)
        conn.autocommit = True
        with conn.cursor() as cursor:
            logger.info("Executing migration to add tarefa and como_fazer columns if not exist...")
            
            # Executar queries de migração
            cursor.execute("ALTER TABLE bsf_metas_plano ADD COLUMN IF NOT EXISTS tarefa TEXT;")
            logger.info("Column 'tarefa' checked/added successfully.")
            
            cursor.execute("ALTER TABLE bsf_metas_plano ADD COLUMN IF NOT EXISTS como_fazer TEXT;")
            logger.info("Column 'como_fazer' checked/added successfully.")
            
        conn.close()
        logger.info("✅ Database migration completed successfully!")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        exit(1)

if __name__ == "__main__":
    run_migration()
