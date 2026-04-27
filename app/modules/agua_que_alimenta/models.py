from typing import Optional
from pydantic import BaseModel, validator
import datetime
from app.services.utils import remover_acentos

# ==============================================================================
# MODELOS DE DADOS - ÁGUA QUE ALIMENTA
# ==============================================================================

class Documento(BaseModel):
    id: int
    nome_documento: str
    descricao: Optional[str] = None
    nome_arquivo: str
    caminho_arquivo: str
    data_upload: str


class CronogramaItemBase(BaseModel):
    tarefa: str
    data_prevista: str
    data_realizada: Optional[str] = None
    status: str
    responsavel: Optional[str] = None
    observacao: Optional[str] = None


class CronogramaItem(CronogramaItemBase):
    id: int


class ValidacaoPendenteItem(BaseModel):
    id: int
    nome_arquivo: Optional[str] = None
    status: str
    data_criacao: datetime.datetime


class Beneficiario(BaseModel):
    id: int
    nome_tecnico: Optional[str] = None
    cpf_tecnico: Optional[str] = None
    municipio: Optional[str] = None
    comunidade: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    data_atividade: Optional[str] = None
    nome_familiar: Optional[str] = None
    cpf_familiar: Optional[str] = None
    nis: Optional[str] = None
    renda_media: Optional[str] = None
    status: Optional[str] = None
    tecnico_agua_que_alimenta: Optional[str] = None
    doc_status: Optional[str] = None
    grh: Optional[str] = None
    verificado_bsf: Optional[str] = None
    nome_completo: Optional[str] = None
    sexo: Optional[str] = None
    data_nascimento: Optional[str] = None
    cpf: Optional[str] = None
    escolaridade: Optional[str] = None
    ref_localizacao: Optional[str] = None
    estado_uf: Optional[str] = None
    pedreiro_id: Optional[int] = None


class BeneficiarioUpdate(BaseModel):
    # Adicione aqui todos os campos que poderão ser editados no formulário
    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
    sexo: Optional[str] = None
    data_nascimento: Optional[str] = None
    municipio: Optional[str] = None
    comunidade: Optional[str] = None
    nis: Optional[str] = None
    grh: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    tecnico_agua_que_alimenta: Optional[str] = None
    verificado_bsf: Optional[str] = None
    renda_media: Optional[str] = None
    pedreiro_id: Optional[int] = None
    faturamento_id: Optional[int] = None

    @validator('municipio', pre=True)
    def normalize_municipio_update(cls, v):
        return remover_acentos(v)

class FaturamentoCreate(BaseModel):
    pedreiro_id: int
    beneficiarios_ids: list[int]
    valor_total: float
    valor_dam: float


class BeneficiarioParaKML(BaseModel):
    id: int  # Ou outro identificador único
    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
    comunidade: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    status: Optional[str] = None


class BeneficiarioValidado(BaseModel):
    id_fila: int
    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[str] = None
    sexo: Optional[str] = None
    escolaridade: Optional[str] = None
    comunidade: Optional[str] = None
    municipio: Optional[str] = None
    estado_uf: Optional[str] = None
    ref_localizacao: Optional[str] = None
    nis: Optional[str] = None


class EventoBase(BaseModel):
    municipio_comunidade: str
    dia_previsto: str
    realizado: bool = False
    observacao: Optional[str] = None
    link_formulario: Optional[str] = None


class Evento(EventoBase):
    id: int
    caminho_arquivo: Optional[str] = None


class EventoStatusUpdate(BaseModel):
    realizado: bool


class PedreiroBase(BaseModel):
    nome_completo: str
    cpf: str
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    dados_pagamento: Optional[str] = None
    status: Optional[str] = 'Ativo'


class PedreiroCreate(PedreiroBase):
    pass


class PedreiroUpdate(BaseModel):
    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    dados_pagamento: Optional[str] = None
    status: Optional[str] = None


class Pedreiro(PedreiroBase):
    id: int
    total_obras: int = 0
    producao_count: int = 0
    ultima_producao: Optional[str] = None
    status_financeiro: Optional[str] = None


class SchemaValidacao(BaseModel):
    id: Optional[int] = None
    id_fila: Optional[str | int] = None

    cpf: str
    nome_completo: Optional[str] = None
    data_nascimento: Optional[str] = None
    escolaridade: Optional[str] = None
    comunidade: Optional[str] = None
    municipio: Optional[str] = None
    nis: Optional[str] = None
    
    uf: Optional[str] = None
    estado_uf: Optional[str] = None

    ref_localizacao: Optional[str] = None
    sexo: Optional[str] = None

    @validator('municipio', pre=True)
    def normalize_municipio_val(cls, v):
        return remover_acentos(v)

    class Config:
        extra = "ignore"
