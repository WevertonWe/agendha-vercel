"""
app/core/auth/dependencies.py
Sistema de Autenticação e Autorização — Supabase-native.

Implementa:
  - Validação JWT com lookup de usuário no Supabase
  - SuperAdmin VIP list (5 usuários imunes a restrições de projeto)
  - RBAC granular por projeto: admin > editor > viewer
  - Bloqueio de escrita (POST/PUT/DELETE) para role 'viewer'
  - Fail-Safe: se o Supabase falhar, o acesso é bloqueado com 503
"""
import logging
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.auth.utils import SECRET_KEY, ALGORITHM
from app.core.auth.models import TokenData, UserInDB, UserProjectRole
from app.config import settings

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------------------------------------------------------------------------
# SuperAdmin VIP — imunes a todas as restrições de projeto
# Ajuste esta lista com os usernames reais do ambiente de produção.
# ---------------------------------------------------------------------------
SUPER_ADMIN_VIP: set[str] = {
    settings.ADMIN_USERNAME,      # admin principal do .env
    "weverton",
    "weverton.wilson",
    "admin",
    "superadmin",
}


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _get_supabase():
    """Importação lazy para evitar circular imports."""
    from app.core.database import get_supabase
    return get_supabase()


def _fetch_user_from_supabase(username: str) -> UserInDB:
    """
    Busca o usuário e suas roles de projeto no Supabase.
    Lança HTTPException 503 se o banco estiver indisponível.
    Lança HTTPException 401 se o usuário não for encontrado.
    """
    try:
        supabase = _get_supabase()

        # Busca o usuário pelo username (case-insensitive)
        res = supabase.table("users") \
                      .select("id, username, full_name, role, is_active, password_hash") \
                      .ilike("username", username) \
                      .maybe_single() \
                      .execute()

        if not res.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": settings.AUTH_BEARER_PREFIX},
            )

        user_data = res.data

        # Busca roles por projeto
        roles_res = supabase.table("user_project_roles") \
                            .select("project_id, role") \
                            .eq("user_id", user_data["id"]) \
                            .execute()

        project_roles = [
            UserProjectRole(project_id=row["project_id"], role=row["role"])
            for row in (roles_res.data or [])
        ]

        return UserInDB(
            username=user_data["username"],
            full_name=user_data.get("full_name"),
            role=user_data.get("role", "user"),
            is_active=bool(user_data.get("is_active", True)),
            hashed_password=user_data.get("password_hash", ""),
            project_roles=project_roles,
        )

    except HTTPException:
        raise  # Re-propaga exceções intencionais

    except Exception as e:
        # Fail-Safe: qualquer falha do Supabase gera 503, nunca 200
        logger.error(f"[Auth] Falha de conexão Supabase ao validar usuário '{username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "O banco de dados está temporariamente indisponível. "
                "Aguarde alguns instantes e tente novamente."
            ),
        )


# ---------------------------------------------------------------------------
# Dependências públicas FastAPI
# ---------------------------------------------------------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Valida o JWT e retorna o usuário correspondente do Supabase.
    Fail-safe: se o Supabase falhar, retorna 503 (nunca permite bypass).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": settings.AUTH_BEARER_PREFIX},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    return _fetch_user_from_supabase(token_data.username)


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Garante que o usuário está ativo."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user


async def get_admin_user(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
    """
    Exige role global 'admin' OU pertencer à lista VIP de SuperAdmins.
    """
    is_super_admin = current_user.username in SUPER_ADMIN_VIP
    is_global_admin = current_user.role == "admin"

    if not (is_super_admin or is_global_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilégios de administrador necessários",
        )
    return current_user


# ---------------------------------------------------------------------------
# RBAC Granular por Projeto
# ---------------------------------------------------------------------------

def _get_project_role(user: UserInDB, project_id: str) -> str:
    """
    Retorna o role do usuário para um projeto específico.
    SuperAdmins recebem sempre 'admin', independente do vínculo.
    Usuários sem vínculo explícito recebem 'viewer' como padrão seguro.
    """
    if user.username in SUPER_ADMIN_VIP or user.role == "admin":
        return "admin"

    for pr in user.project_roles:
        if pr.project_id == project_id:
            return pr.role

    return "viewer"  # Padrão seguro: sem vínculo = somente leitura


def require_project_access(project_id: str, min_role: str = "viewer"):
    """
    Factory de dependência que exige acesso mínimo a um projeto.

    Hierarquia de roles: viewer < editor < admin

    Uso nas rotas:
        @router.get("/", dependencies=[Depends(require_project_access("financeiro"))])
        @router.post("/", dependencies=[Depends(require_project_access("financeiro", "editor"))])
        @router.delete("/", dependencies=[Depends(require_project_access("financeiro", "admin"))])
    """
    ROLE_HIERARCHY = {"viewer": 0, "editor": 1, "admin": 2}

    async def _dependency(current_user: UserInDB = Depends(get_current_active_user)):
        user_role = _get_project_role(current_user, project_id)
        user_level = ROLE_HIERARCHY.get(user_role, 0)
        required_level = ROLE_HIERARCHY.get(min_role, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Acesso negado ao projeto '{project_id}'. "
                    f"Nível exigido: '{min_role}'. Seu nível: '{user_role}'."
                ),
            )
        return current_user

    return _dependency


def block_viewers(request: Request, current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
    """
    Dependência global que bloqueia métodos de escrita (POST/PUT/DELETE/PATCH)
    para usuários com role global 'viewer'.

    SuperAdmins e admins passam sempre. Editores passam.
    Viewers recebem 403 em qualquer rota de escrita.

    Uso nas rotas (injetar no router ou por rota individual):
        router = APIRouter(dependencies=[Depends(block_viewers)])
    """
    write_methods = {"POST", "PUT", "DELETE", "PATCH"}
    is_write = request.method.upper() in write_methods
    is_viewer = current_user.role == "viewer"
    is_vip = current_user.username in SUPER_ADMIN_VIP

    if is_write and is_viewer and not is_vip:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuários com perfil 'viewer' não podem realizar operações de escrita.",
        )
    return current_user
