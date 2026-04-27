from typing import Optional
from pydantic import BaseModel

class MaterialBase(BaseModel):
    nome: str
    unidade: str
    categoria: Optional[str] = None
    descricao: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    nome: Optional[str] = None
    unidade: Optional[str] = None
    categoria: Optional[str] = None
    descricao: Optional[str] = None

class Material(MaterialBase):
    id: int

    class Config:
        from_attributes = True
