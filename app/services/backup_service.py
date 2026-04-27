import shutil
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = 'agendha.db'
BACKUP_DIR = 'backups'

def create_snapshot(reason: str) -> str:
    """
    Creates a backup copy of the database.
    
    Args:
        reason (str): A short string describing the reason for the backup (e.g., 'grh_lote').
        
    Returns:
        str: The path to the created backup file.
        
    Raises:
        FileNotFoundError: If the source database file does not exist.
        IOError: If there is an error during the copy process.
    """
    if not os.path.exists(DB_PATH):
        logger.error(f"Source database not found at {DB_PATH}")
        raise FileNotFoundError(f"Source database not found at {DB_PATH}")

    # Ensure backup directory exists
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR)
            logger.info(f"Created backup directory at {BACKUP_DIR}")
        except OSError as e:
            logger.error(f"Failed to create backup directory: {e}")
            raise

    # Generate timestamp and filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize reason text
    safe_reason = "".join(c for c in reason if c.isalnum() or c in ('_', '-')).strip()
    filename = f"backup_agendha_{timestamp}_{safe_reason}.db"
    destination_path = os.path.join(BACKUP_DIR, filename)

    try:
        shutil.copy2(DB_PATH, destination_path)
        logger.info(f"Database snapshot created: {destination_path}")
        return destination_path
    except IOError as e:
        logger.error(f"Failed to copy database file: {e}")
        raise
