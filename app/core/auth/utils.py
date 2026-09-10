from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.config import settings

# --- Configurações JWT ---
SECRET_KEY = settings.SECRET_KEY # Lê do .env
ALGORITHM = getattr(settings, "ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SUPER_ADMIN_VIP: set[str] = {
    getattr(settings, "ADMIN_USERNAME", "admin"),
    "weverton",
    "weverton.wilson",
    "admin",
    "superadmin",
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def extract_token_from_request(request) -> Optional[str]:
    """Extrai token JWT do cookie ou header Authorization."""
    if not request:
        return None
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header
    if token:
        bearer_prefix = getattr(settings, "AUTH_BEARER_PREFIX", "Bearer")
        if token.startswith(f"{bearer_prefix} "):
            token = token[len(bearer_prefix) + 1:].strip()
        elif token.startswith("Bearer "):
            token = token[7:].strip()
    return token

def get_user_context_from_request(request, default_context_project: Optional[str] = None) -> dict:
    """
    Extrai contexto do usuário (is_admin, user_username, user_role) 100% em memória via JWT.
    Zero chamadas de rede para máxima performance e concorrência sem bloqueio.
    """
    is_admin = False
    user_username = "Anônimo"
    user_role = "user"
    
    token = extract_token_from_request(request)
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_username = payload.get("sub") or "Anônimo"
            user_role = payload.get("role", "user")
            
            if user_role == "admin" or str(user_username).strip().lower() in {str(u).strip().lower() for u in SUPER_ADMIN_VIP if u}:
                is_admin = True
        except Exception:
            pass
            
    ctx = {
        "is_admin": is_admin,
        "user_username": user_username,
        "user_role": user_role
    }
    if default_context_project:
        ctx["context_project"] = default_context_project
    return ctx

