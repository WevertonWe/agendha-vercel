from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from app.config import settings
from app.core.auth.models import (
    Token, User, UserCreate, UserUpdate, UserInDB, TrocarSenhaSchema
)
from app.core.auth.dependencies import get_current_user, get_admin_user
from app.core.auth.utils import (
    create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
)

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", truncate_error=True
)

router = APIRouter(tags=["Autenticação"])

# SuperAdmins VIP — ações registradas no audit_logs
VIP_SUPERADMINS = {"admin", "weverton", "marilac", "maciel", "fabiano"}

_ERRO_GENERICO = "Usuário ou senha inválidos"


def _get_supabase():
    from app.core.database import get_supabase
    return get_supabase()


def _audit_vip_login(username: str, ip: str | None = None) -> None:
    """Registra no audit_logs quando um SuperAdmin VIP autentica."""
    if username.lower() not in VIP_SUPERADMINS:
        return
    try:
        from app.core.logging.services import log_acao
        log_acao(
            acao="VIP_LOGIN",
            modulo="auth",
            user_id=username,
            ip=ip,
            nivel="WARNING",
            detalhes={"evento": "SuperAdmin VIP autenticado com sucesso"},
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(
            f"[AuditVIP] Falha ao registrar login VIP: {e}"
        )


@router.post("/api/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    username_lower = form_data.username.strip().lower()
    client_ip = request.client.host if request.client else None

    supabase = _get_supabase()

    try:
        res = (
            supabase.table("users")
            .select("*")
            .eq("username", username_lower)
            .execute()
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(
            f"[Auth] Falha na consulta Supabase: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_ERRO_GENERICO,
            headers={"WWW-Authenticate": settings.AUTH_BEARER_PREFIX},
        )

    # Segurança: mesmo erro para usuário inexistente e senha errada
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_ERRO_GENERICO,
            headers={"WWW-Authenticate": settings.AUTH_BEARER_PREFIX},
        )

    user_dict = res.data[0]
    db_hash = user_dict.get("password_hash", "").strip()

    if not pwd_context.verify(str(form_data.password), str(db_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_ERRO_GENERICO,
            headers={"WWW-Authenticate": settings.AUTH_BEARER_PREFIX},
        )

    role = user_dict.get("role", "user")
    canonical_username = user_dict.get("username", username_lower)

    access_token = create_access_token(
        data={"sub": canonical_username, "role": role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Auditoria VIP — fire-and-forget
    _audit_vip_login(canonical_username, ip=client_ip)

    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "redirect_url": "/hub",
    })
    response.set_cookie(
        key="access_token",
        value=f"{settings.AUTH_BEARER_PREFIX} {access_token}",
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/api/auth/change-password")
async def change_password(
    dados: TrocarSenhaSchema,
    current_user: UserInDB = Depends(get_current_user),
):
    from app.core.auth.services import mudar_senha
    mudar_senha(current_user.username, dados)
    return {"message": "Senha alterada com sucesso"}


@router.get("/api/users", response_model=List[User])
async def list_users(current_user: UserInDB = Depends(get_admin_user)):
    supabase = _get_supabase()
    users_res = supabase.table("users").select("*").execute()
    return [
        User(
            username=u.get("username"),
            full_name=u.get("full_name", ""),
            role=u.get("role", "user"),
            is_active=bool(u.get("is_active", True)),
            project_roles=[],
        )
        for u in users_res.data
    ]


@router.post("/api/users", response_model=User)
async def create_user(
    new_user: UserCreate,
    current_user: UserInDB = Depends(get_admin_user),
):
    supabase = _get_supabase()
    username_lower = new_user.username.strip().lower()

    existing = (
        supabase.table("users")
        .select("id")
        .eq("username", username_lower)
        .execute()
    )
    if existing.data:
        raise HTTPException(
            status_code=400,
            detail=f"O nome de usuário '{username_lower}' já está em uso.",
        )

    hashed_password = get_password_hash(new_user.password)
    payload = {
        "username": username_lower,
        "password_hash": hashed_password,
        "role": new_user.role,
        "is_active": True,
        "full_name": new_user.full_name,
    }

    try:
        supabase.table("users").insert(payload).execute()
        return User(
            username=username_lower,
            role=new_user.role,
            is_active=True,
            full_name=new_user.full_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {e}")


@router.put("/api/users/{username}", response_model=User)
async def update_user(
    username: str,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_admin_user),
):
    supabase = _get_supabase()
    username_lower = username.strip().lower()

    existing = (
        supabase.table("users")
        .select("*")
        .eq("username", username_lower)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    current_data = existing.data[0]

    if username_lower == current_user.username.lower():
        if (
            user_update.role is not None
            and user_update.role != current_data.get("role")
        ):
            raise HTTPException(
                status_code=400, detail="Não pode alterar seu próprio papel"
            )
        if user_update.is_active is False:
            raise HTTPException(
                status_code=400, detail="Não pode desativar a si mesmo"
            )

    updates: dict = {}
    if user_update.full_name is not None:
        updates["full_name"] = user_update.full_name
    if user_update.role is not None:
        updates["role"] = user_update.role
    if user_update.is_active is not None:
        updates["is_active"] = user_update.is_active
    if user_update.password:
        updates["password_hash"] = get_password_hash(user_update.password)

    if not updates:
        return User(
            username=current_data["username"],
            full_name=current_data.get("full_name", ""),
            role=current_data.get("role", "user"),
            is_active=bool(current_data.get("is_active", True)),
        )

    try:
        (
            supabase.table("users")
            .update(updates)
            .eq("username", username_lower)
            .execute()
        )
        updated = (
            supabase.table("users")
            .select("*")
            .eq("username", username_lower)
            .execute()
        )
        u = updated.data[0]
        return User(
            username=u["username"],
            full_name=u.get("full_name", ""),
            role=u.get("role", "user"),
            is_active=bool(u.get("is_active", True)),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar usuário: {e}"
        )


@router.delete("/api/users/{username}", status_code=204)
async def delete_user(
    username: str,
    current_user: UserInDB = Depends(get_admin_user),
):
    username_lower = username.strip().lower()

    if username_lower == current_user.username.lower():
        raise HTTPException(
            status_code=400, detail="Você não pode excluir a si mesmo."
        )

    supabase = _get_supabase()
    existing = (
        supabase.table("users")
        .select("id")
        .eq("username", username_lower)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    try:
        (
            supabase.table("users")
            .delete()
            .eq("username", username_lower)
            .execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao excluir usuário: {e}"
        )
