from typing import Optional
from pydantic import BaseModel, validator
from app.services.utils import remover_acentos, limpar_cpf

class BeneficiarioCisternaBase(BaseModel):
    nome_completo: str
    cpf: Optional[str] = None
    rg: Optional[str] = None
    nis: Optional[str] = None
    telefone: Optional[str] = None
    municipio: Optional[str] = "GLÓRIA"
    comunidade: Optional[str] = None
    implementacao: Optional[str] = "CISTERNA DE CONSUMO 16M³"
    contrato: Optional[str] = "040/2024 – SEADES/AGENDHA"
    status: Optional[str] = "Ativo"
    observacoes: Optional[str] = None

    @validator('nome_completo')
    def validate_nome(cls, v):
        if not v or not v.strip():
            raise ValueError("O nome do beneficiário é obrigatório.")
        return v.strip().upper()

    @validator('cpf', pre=True)
    def validate_cpf(cls, v):
        if v:
            clean = limpar_cpf(str(v))
            if len(clean) == 11:
                return f"{clean[:3]}.{clean[3:6]}.{clean[6:9]}-{clean[9:]}"
            return str(v).strip()
        return None

    @validator('municipio', pre=True)
    def normalize_municipio(cls, v):
        if v:
            return str(v).strip().upper()
        return "GLÓRIA"

    @validator('comunidade', pre=True)
    def normalize_comunidade(cls, v):
        if v:
            return str(v).strip().upper()
        return None


class BeneficiarioCisternaCreate(BeneficiarioCisternaBase):
    pass


class BeneficiarioCisternaUpdate(BaseModel):
    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    nis: Optional[str] = None
    telefone: Optional[str] = None
    municipio: Optional[str] = None
    comunidade: Optional[str] = None
    implementacao: Optional[str] = None
    contrato: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None


class BeneficiarioCisterna(BeneficiarioCisternaBase):
    id: int
    data_cadastro: Optional[str] = None
