from typing import Optional, List
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    redirect_url: Optional[str] = None

class TokenData(BaseModel):
    username: Optional[str] = None

class UserProjectRole(BaseModel):
    project_id: str
    role: str

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: str # Global role (e.g. admin, user)
    is_active: bool
    project_roles: List[UserProjectRole] = []

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    role: str = "user"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class TrocarSenhaSchema(BaseModel):
    senha_atual: str
    nova_senha: str
    confirmar_senha: str
