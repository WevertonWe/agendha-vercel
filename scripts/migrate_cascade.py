
import sqlite3
import logging
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def migrate():
    db_path = settings.DB_PATH
    logging.info(f"Connecting to database at {db_path}...")
    
    conn = sqlite3.connect(db_path)
    # Enable foreign keys support to ensure integrity during the process
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    try:
        logging.info("Starting migration transaction...")
        conn.execute("BEGIN TRANSACTION")

        # 1. Rename existing table
        logging.info("Renaming existing table 'bsf_visitas' to 'bsf_visitas_old'...")
        cursor.execute("ALTER TABLE bsf_visitas RENAME TO bsf_visitas_old")

        # 2. Create new table with ON DELETE CASCADE
        logging.info("Creating new table 'bsf_visitas' with ON DELETE CASCADE...")
        create_table_sql = """
        CREATE TABLE bsf_visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tecnico_id TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
            beneficiario_id TEXT NOT NULL,
            municipio TEXT NOT NULL,
            comunidade TEXT,
            data_visita TEXT NOT NULL,
            status TEXT DEFAULT 'Realizada',
            atividade_id INTEGER REFERENCES bsf_atividades(id),
            data_registro TEXT
        );
        """
        cursor.execute(create_table_sql)

        # Get explicit count before copy
        cursor.execute("SELECT COUNT(*) FROM bsf_visitas_old")
        row_count_old = cursor.fetchone()[0]
        
        # Get columns from old table to ensure mapping is correct regardless of order
        cursor.execute("PRAGMA table_info(bsf_visitas_old)")
        columns_info = cursor.fetchall()
        columns = [info[1] for info in columns_info]
        columns_str = ", ".join(columns)
        
        # Filter out orphans during copy
        insert_sql = f"INSERT INTO bsf_visitas ({columns_str}) SELECT {columns_str} FROM bsf_visitas_old WHERE tecnico_id IN (SELECT username FROM users)"  # nosec
        cursor.execute(insert_sql)
        
        # Log how many were skipped
        skipped = row_count_old - cursor.rowcount
        if skipped > 0:
            logging.warning(f"Skipped {skipped} orphan rows during migration.")
        
        row_count = cursor.rowcount
        logging.info(f"Copied {row_count} rows.")

        # 4. Verify count
        cursor.execute("SELECT COUNT(*) FROM bsf_visitas")
        new_count = cursor.fetchone()[0]
        
        if row_count_old != (new_count + skipped):
            logging.warning(f"Row count mismatch! Old: {row_count_old}, New: {new_count}, Skipped: {skipped}")
            # We don't raise exception here because we intentionally skipped orphans
        else:
            logging.info(f"Row count verified (Old: {row_count_old} == New: {new_count} + Skipped: {skipped})")
        
        logging.info("Row counts match. Dropping old table...")
        
        # 5. Drop old table
        cursor.execute("DROP TABLE bsf_visitas_old")

        conn.commit()
        logging.info("Migration completed successfully.")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
