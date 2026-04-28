import sqlite3
import json
import logging
from typing import Any, Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)

def log_change(
    db: sqlite3.Connection,
    tabela: str,
    registro_id: int,
    operacao: str,
    valor_antigo: Optional[Dict[str, Any]],
    valor_novo: Optional[Dict[str, Any]],
    usuario_id: str = "SYSTEM",
    detalhes: Optional[str] = None
):
    """
    Logs a change to the audit_logs table.

    Args:
        db (sqlite3.Connection): Active database connection.
        tabela (str): Name of the table being modified.
        registro_id (int): ID of the record being modified.
        operacao (str): Type of operation ('INSERT', 'UPDATE', 'DELETE').
        valor_antigo (dict): The state of the record before change (None for INSERT).
        valor_novo (dict): The state of the record after change (None for DELETE).
        usuario_id (str): Identifier of the user performing the action.
        detalhes (str): Optional metadata or comments.
    """
    try:
        import os
        if os.getenv("VERCEL"):
            logger.info("Vercel detected. Bypassing SQLite audit log.")
            return

        from app.core.time_utils import get_bahia_time_str
        
        sql = """
            INSERT INTO audit_logs (
                usuario_id, tabela, registro_id, operacao, 
                valor_antigo, valor_novo, detalhes, data_hora
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Serialize dicts to JSON
        old_val_json = json.dumps(valor_antigo, default=str) if valor_antigo is not None else None
        new_val_json = json.dumps(valor_novo, default=str) if valor_novo is not None else None

        db.execute(sql, (
            usuario_id, 
            tabela, 
            registro_id, 
            operacao, 
            old_val_json, 
            new_val_json, 
            detalhes,
            get_bahia_time_str()
        ))
        # Commit should be handled by the caller transaction, but if this is standalone:
        # db.commit() 
    except sqlite3.Error as e:
        logger.error(f"Failed to write audit log: {e}")
        # We generally don't want audit failure to break the main transaction, 
        # but for high security it should. For this app, we'll log exception but re-raise 
        # to ensure integrity if strictness is required.
        raise
