import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = "agendha.db"

def migrate_db():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        logging.info("Checking for 'status_pagamento' column in 'beneficiarios'...")
        try:
            cursor.execute("ALTER TABLE beneficiarios ADD COLUMN status_pagamento TEXT DEFAULT 'PENDENTE'")
            logging.info("Added 'status_pagamento' column.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("'status_pagamento' column already exists. Skipping.")
            else:
                logging.error(f"Error adding 'status_pagamento': {e}")

        logging.info("Checking for 'link_nota_fiscal' column in 'beneficiarios'...")
        try:
            cursor.execute("ALTER TABLE beneficiarios ADD COLUMN link_nota_fiscal TEXT")
            logging.info("Added 'link_nota_fiscal' column.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("'link_nota_fiscal' column already exists. Skipping.")
            else:
                logging.error(f"Error adding 'link_nota_fiscal': {e}")
        
        logging.info("Checking for 'data_conclusao' column in 'beneficiarios'...")
        try:
            cursor.execute("ALTER TABLE beneficiarios ADD COLUMN data_conclusao DATE")
            logging.info("Added 'data_conclusao' column.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("'data_conclusao' column already exists. Skipping.")
            else:
                logging.error(f"Error adding 'data_conclusao': {e}")

        conn.commit()
        conn.close()
        logging.info("Migration completed successfully.")

    except Exception as e:
        logging.error(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_db()
