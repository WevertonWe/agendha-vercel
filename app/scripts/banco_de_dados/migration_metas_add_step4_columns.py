import os
import psycopg2
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    # Carregar .env
    load_dotenv()

    db_string = os.getenv("SUPABASE_DB_STRING")
    if not db_string:
        logger.error("CRITICAL: SUPABASE_DB_STRING is not set in environment or .env!")
        exit(1)

    logger.info("Connecting to Supabase Database...")
    try:
        conn = psycopg2.connect(db_string)
        conn.autocommit = True
        with conn.cursor() as cursor:
            logger.info("Executing migration to add 'entrega' and 'recursos_necessarios' columns if not exist...")
            
            # Adicionar coluna entrega
            cursor.execute("ALTER TABLE bsf_metas_plano ADD COLUMN IF NOT EXISTS entrega TEXT;")
            logger.info("Column 'entrega' checked/added successfully.")
            
            # Adicionar coluna recursos_necessarios
            cursor.execute("ALTER TABLE bsf_metas_plano ADD COLUMN IF NOT EXISTS recursos_necessarios TEXT;")
            logger.info("Column 'recursos_necessarios' checked/added successfully.")
            
        conn.close()
        logger.info("✅ Database migration completed successfully!")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        exit(1)

if __name__ == "__main__":
    run_migration()
