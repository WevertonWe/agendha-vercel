"""
app/services/store.py
Fila de Validação OCR — Supabase-native implementation.

Substitui o JSON local (/tmp/fila_validacao.json) pela tabela
`ocr_fila_validacao` no Supabase, eliminando dados voláteis entre
invocações serverless na Vercel.

Schema esperado (Supabase SQL):
    CREATE TABLE ocr_fila_validacao (
        id           TEXT PRIMARY KEY,
        dados        JSONB NOT NULL,
        data_criacao TIMESTAMPTZ DEFAULT NOW()
    );
"""
import logging
from typing import Any, Dict, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _get_supabase():
    """Importação lazy para evitar circular imports."""
    from app.core.database import get_supabase
    return get_supabase()


# ---------------------------------------------------------------------------
# Interface pública (mantém contrato com callers existentes)
# ---------------------------------------------------------------------------

def load_queue() -> List[Dict[str, Any]]:
    """Retorna todos os itens da fila de validação, ordenados por data (desc)."""
    try:
        supabase = _get_supabase()
        res = supabase.table("ocr_fila_validacao") \
                      .select("id, dados, data_criacao") \
                      .order("data_criacao", desc=True) \
                      .execute()
        rows = res.data or []
        # Flatten: mescla os campos de 'dados' com 'id' e 'data_criacao'
        result = []
        for row in rows:
            item = dict(row.get("dados") or {})
            item["id"] = row["id"]
            item["data_criacao"] = row.get("data_criacao")
            result.append(item)
        return result
    except Exception as e:
        logger.error(f"Erro ao carregar fila OCR do Supabase: {e}")
        return []


def save_queue(queue: List[Dict[str, Any]]) -> None:
    """
    Sincroniza a lista completa com o Supabase.
    Cada item deve ter um campo 'id'.
    Itens sem 'id' são ignorados com aviso.
    """
    try:
        supabase = _get_supabase()
        for item in queue:
            item_id = item.get("id")
            if not item_id:
                logger.warning("Item sem 'id' ignorado ao salvar fila.")
                continue
            payload = {k: v for k, v in item.items() if k not in ("id", "data_criacao")}
            supabase.table("ocr_fila_validacao").upsert(
                {"id": str(item_id), "dados": payload},
                on_conflict="id"
            ).execute()
    except Exception as e:
        logger.error(f"Erro ao salvar fila OCR no Supabase: {e}")


def add_to_queue(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adiciona (ou sobrescreve) um item na fila de validação.
    Gera 'id' automático se ausente. Usa upsert para idempotência.
    """
    try:
        if "id" not in item:
            item["id"] = str(int(datetime.now(tz=timezone.utc).timestamp() * 1000))
        if "data_criacao" not in item:
            item["data_criacao"] = datetime.now(tz=timezone.utc).isoformat()

        supabase = _get_supabase()
        # Separa metadados do payload de dados
        payload = {k: v for k, v in item.items() if k not in ("id", "data_criacao")}
        supabase.table("ocr_fila_validacao").upsert(
            {"id": str(item["id"]), "dados": payload},
            on_conflict="id"
        ).execute()
        return item
    except Exception as e:
        logger.error(f"Erro ao adicionar item na fila OCR: {e}")
        return item


def get_item(item_id: str) -> Dict[str, Any]:
    """Busca um item pelo ID. Retorna None se não encontrado."""
    try:
        supabase = _get_supabase()
        res = supabase.table("ocr_fila_validacao") \
                      .select("id, dados, data_criacao") \
                      .eq("id", str(item_id)) \
                      .maybe_single() \
                      .execute()
        if not res.data:
            return None
        row = res.data
        item = dict(row.get("dados") or {})
        item["id"] = row["id"]
        item["data_criacao"] = row.get("data_criacao")
        return item
    except Exception as e:
        logger.error(f"Erro ao buscar item '{item_id}' na fila OCR: {e}")
        return None


def delete_item(item_id: str) -> bool:
    """
    Remove um item da fila pelo ID.
    Retorna True se o item foi encontrado e removido.
    """
    try:
        supabase = _get_supabase()
        res = supabase.table("ocr_fila_validacao") \
                      .delete() \
                      .eq("id", str(item_id)) \
                      .execute()
        return bool(res.data)
    except Exception as e:
        logger.error(f"Erro ao remover item '{item_id}' da fila OCR: {e}")
        return False
