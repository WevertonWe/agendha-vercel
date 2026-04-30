from fastapi import HTTPException
from app.core.auth.models import TrocarSenhaSchema
from app.core.auth.utils import verify_password, get_password_hash


def _get_supabase():
    from app.core.database import get_supabase
    return get_supabase()


def mudar_senha(username: str, dados: TrocarSenhaSchema) -> None:
    """
    Troca a senha de um usuário autenticado via Supabase.
    Valida senha atual antes de gravar o novo hash.
    """
    supabase = _get_supabase()

    res = (
        supabase.table("users")
        .select("password_hash")
        .eq("username", username.lower())
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    current_hash = res.data[0].get("password_hash", "")

    if not verify_password(dados.senha_atual, current_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    if dados.nova_senha != dados.confirmar_senha:
        raise HTTPException(
            status_code=400, detail="As novas senhas não conferem"
        )

    new_hash = get_password_hash(dados.nova_senha)

    try:
        (
            supabase.table("users")
            .update({"password_hash": new_hash})
            .eq("username", username.lower())
            .execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar senha: {e}"
        )
