"""
app/core/logging/services.py
Sistema de Auditoria e Observabilidade — Supabase-native.

Substitui a gravação SQLite local por uma tabela `audit_logs` no Supabase.

Princípios de design:
  - Não-bloqueante: erros de log NUNCA interrompem a rota principal.
  - Fire-and-forget: gravação assíncrona via asyncio.create_task quando possível.
  - Metadados de IA: campo `ia_tokens` + `ia_modelo` para rastreamento de consumo.
  - Compatibilidade retroativa: mantém `insert_log()` para callers legados.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core interno — não chamar diretamente, use as funções públicas abaixo
# ---------------------------------------------------------------------------

def _get_supabase():
    """Importação lazy para evitar circular imports no boot."""
    from app.core.database import get_supabase
    return get_supabase()


def _gravar_log(payload: Dict[str, Any]) -> None:
    """
    Grava um registro na tabela `audit_logs` do Supabase.
    Silencioso em caso de falha — nunca propaga exceções.
    """
    try:
        supabase = _get_supabase()
        supabase.table("audit_logs").insert(payload).execute()
    except Exception as e:
        # Fail-safe: erro de logging NUNCA deve crashar a aplicação
        logger.warning(f"[AuditLog] Falha ao gravar log no Supabase (non-fatal): {e}")


# ---------------------------------------------------------------------------
# Interface pública principal
# ---------------------------------------------------------------------------

def log_acao(
    acao: str,
    modulo: str = "core",
    user_id: str = "SYSTEM",
    tabela: Optional[str] = None,
    registro_id: Optional[str] = None,
    detalhes: Optional[Dict[str, Any]] = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    ia_tokens: int = 0,
    ia_modelo: Optional[str] = None,
    duracao_ms: Optional[int] = None,
    nivel: str = "INFO",
) -> None:
    """
    Registra uma ação crítica no sistema de auditoria Supabase.

    Uso mínimo:
        log_acao("LOGIN", modulo="auth", user_id="joao", ip="192.168.1.1")

    Com metadados de IA:
        log_acao(
            "IA_REQUEST",
            modulo="ocr",
            user_id=current_user,
            ia_tokens=230,
            ia_modelo="gemini-2.0-flash",
            duracao_ms=1850,
            detalhes={"prompt_tokens": 150, "completion_tokens": 80}
        )
    """
    payload: Dict[str, Any] = {
        "user_id": str(user_id),
        "acao": acao,
        "modulo": modulo,
        "nivel": nivel,
    }

    # Campos opcionais — incluir apenas se fornecidos
    if tabela:
        payload["tabela"] = tabela
    if registro_id is not None:
        payload["registro_id"] = str(registro_id)
    if detalhes:
        payload["detalhes"] = detalhes
    if ip:
        payload["ip"] = ip
    if user_agent:
        payload["user_agent"] = user_agent
    if ia_tokens:
        payload["ia_tokens"] = ia_tokens
    if ia_modelo:
        payload["ia_modelo"] = ia_modelo
    if duracao_ms is not None:
        payload["duracao_ms"] = duracao_ms

    _gravar_log(payload)


def log_erro(
    mensagem: str,
    modulo: str = "core",
    user_id: str = "SYSTEM",
    detalhes: Optional[Dict[str, Any]] = None,
    ip: Optional[str] = None,
) -> None:
    """
    Atalho para registrar erros críticos.

    log_erro("Falha na geração de PDF", modulo="atestes", user_id=current_user)
    """
    log_acao(
        acao="ERROR",
        modulo=modulo,
        user_id=user_id,
        detalhes={"mensagem": mensagem, **(detalhes or {})},
        ip=ip,
        nivel="ERROR",
    )


def log_ia(
    modulo: str,
    user_id: str,
    modelo: str,
    prompt_tokens: int,
    completion_tokens: int,
    duracao_ms: Optional[int] = None,
    detalhes: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Atalho para rastrear consumo de IA por requisição.

    log_ia(
        modulo="ocr",
        user_id=current_user,
        modelo="gemini-2.0-flash",
        prompt_tokens=150,
        completion_tokens=80,
        duracao_ms=1850
    )
    """
    total_tokens = prompt_tokens + completion_tokens
    log_acao(
        acao="IA_REQUEST",
        modulo=modulo,
        user_id=user_id,
        ia_tokens=total_tokens,
        ia_modelo=modelo,
        duracao_ms=duracao_ms,
        nivel="INFO",
        detalhes={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            **(detalhes or {}),
        },
    )


# ---------------------------------------------------------------------------
# Compatibilidade retroativa (callers legados que chamavam insert_log)
# ---------------------------------------------------------------------------

def insert_log(usuario: str, rota: str, metodo: str, ip_origem: str) -> None:
    """
    [LEGADO] Mantido para compatibilidade. Usa log_acao internamente.
    Novos callers devem usar log_acao() diretamente.
    """
    log_acao(
        acao=f"HTTP_{metodo.upper()}",
        modulo="http_access",
        user_id=usuario or "ANONYMOUS",
        ip=ip_origem,
        detalhes={"rota": rota, "metodo": metodo},
        nivel="INFO",
    )
