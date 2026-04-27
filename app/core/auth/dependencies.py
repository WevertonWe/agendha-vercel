from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import sqlite3

from app.core.database import get_db_connection
from app.core.auth.utils import SECRET_KEY, ALGORITHM
from app.core.auth.models import TokenData, UserInDB, UserProjectRole
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: sqlite3.Connection = Depends(get_db_connection)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": settings.AUTH_BEARER_PREFIX},  # nosec
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (token_data.username,))
    user_row = cursor.fetchone()
    if user_row is None:
        raise credentials_exception
    
    # Converter row para dict
    user_dict = dict(user_row)
    
    # Buscar roles por projeto
    cursor.execute("SELECT project_id, role FROM user_project_roles WHERE user_id = ?", (user_dict['id'],))
    roles_rows = cursor.fetchall()
    project_roles = [UserProjectRole(project_id=row['project_id'], role=row['role']) for row in roles_rows]

    return UserInDB(
        username=user_dict['username'],
        full_name=user_dict['full_name'],
        role=user_dict['role'],
        is_active=bool(user_dict['is_active']),
        hashed_password=user_dict['password_hash'],
        project_roles=project_roles
    )

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user

async def get_admin_user(current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilégios de administrador necessários"
        )
    return current_user
