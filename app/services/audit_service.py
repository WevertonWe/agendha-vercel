"""
app/services/audit_service.py
Serviço de Auditoria de Dados — Supabase-native.

Rastreia operações de escrita (INSERT, UPDATE, DELETE) em tabelas críticas,
armazenando valor_antigo e valor_novo em JSONB no Supabase.

Compatibilidade: mantém a assinatura `log_change()` para callers existentes,
mas remove a dependência de `sqlite3.Connection`.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _get_supabase():
    """Importação lazy para evitar circular imports."""
    from app.core.database import get_supabase
    return get_supabase()


def log_change(
    db: Any,  # Mantido por compatibilidade — ignorado (não é mais sqlite3.Connection)
    tabela: str,
    registro_id: Any,
    operacao: str,
    valor_antigo: Optional[Dict[str, Any]],
    valor_novo: Optional[Dict[str, Any]],
    usuario_id: str = "SYSTEM",
    detalhes: Optional[str] = None,
) -> None:
    """
    Registra uma mudança de dado na tabela `audit_logs` do Supabase.

    O parâmetro `db` é mantido por compatibilidade retroativa com callers
    que passavam sqlite3.Connection — ele é ignorado nesta implementação.

    Args:
        db:           (ignorado) Legado SQLite connection.
        tabela:       Nome da tabela afetada (ex: 'beneficiarios').
        registro_id:  ID do registro modificado.
        operacao:     'INSERT', 'UPDATE', ou 'DELETE'.
        valor_antigo: Estado antes da mudança (None para INSERT).
        valor_novo:   Estado após a mudança (None para DELETE).
        usuario_id:   Identificador do usuário.
        detalhes:     Texto livre de contexto adicional.
    """
    try:
        payload = {
            "user_id": str(usuario_id),
            "acao": operacao.upper(),
            "modulo": "data_change",
            "tabela": tabela,
            "registro_id": str(registro_id) if registro_id is not None else None,
            "nivel": "INFO",
            "detalhes": {
                "valor_antigo": valor_antigo,
                "valor_novo": valor_novo,
                "nota": detalhes,
            },
        }

        supabase = _get_supabase()
        supabase.table("audit_logs").insert(payload).execute()

    except Exception as e:
        # Fail-safe: auditoria nunca deve quebrar a operação principal
        logger.warning(f"[AuditLog] Falha ao gravar audit log (non-fatal): {e}")
