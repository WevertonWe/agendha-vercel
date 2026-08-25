from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator
import datetime
from app.services.utils import remover_acentos

# ==============================================================================
# MODELOS DE DADOS - PROJETO P1+2
# ==============================================================================

# --- BENEFICIÁRIOS P1+2 ---
class BeneficiarioP12Base(BaseModel):
    nome_completo: Optional[str] = None
    nome_familiar: Optional[str] = None
    cpf: Optional[str] = None
    cpf_familiar: Optional[str] = None
    nis: Optional[str] = None
    data_nascimento: Optional[str] = None
    sexo: Optional[str] = None
    escolaridade: Optional[str] = None
    municipio: Optional[str] = None
    comunidade: Optional[str] = None
    estado_uf: Optional[str] = "BA"
    ref_localizacao: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    status: Optional[str] = "Ativo"
    doc_status: Optional[str] = "Pendente"
    observacoes: Optional[str] = None

    @validator('municipio', pre=True)
    def normalize_municipio(cls, v):
        if v:
            return remover_acentos(str(v))
        return v

class BeneficiarioP12Create(BeneficiarioP12Base):
    pass

class BeneficiarioP12Update(BeneficiarioP12Base):
    pass

class BeneficiarioP12(BeneficiarioP12Base):
    id: int
    data_cadastro: Optional[str] = None


# --- MONITORAMENTO P1+2 (GAPA, SISMA, INTERCÂMBIO) ---
class MonitoramentoBase(BaseModel):
    tipo: str # 'GAPA', 'SISMA', 'INTERCAMBIO'
    titulo: str
    data_evento: Optional[str] = None
    municipio: Optional[str] = None
    comunidade: Optional[str] = None
    responsavel: Optional[str] = None
    status: Optional[str] = "Realizado"
    quantidade_participantes: Optional[int] = 0
    participantes_ids: Optional[str] = "[]"
    participantes_nomes: Optional[str] = None
    observacao: Optional[str] = None
    link_documento: Optional[str] = None


    @validator('tipo')
    def validate_tipo(cls, v):
        v_upper = v.upper().strip()
        if v_upper not in ['GAPA', 'SISMA', 'INTERCAMBIO', 'INTERCÂMBIO']:
            raise ValueError("Tipo inválido. Deve ser GAPA, SISMA ou INTERCAMBIO.")
        if v_upper == 'INTERCÂMBIO':
            return 'INTERCAMBIO'
        return v_upper

class MonitoramentoCreate(MonitoramentoBase):
    pass

class MonitoramentoUpdate(BaseModel):
    tipo: Optional[str] = None
    titulo: Optional[str] = None
    data_evento: Optional[str] = None
    municipio: Optional[str] = None
    comunidade: Optional[str] = None
    responsavel: Optional[str] = None
    status: Optional[str] = None
    quantidade_participantes: Optional[int] = None
    participantes_ids: Optional[str] = None
    participantes_nomes: Optional[str] = None
    observacao: Optional[str] = None
    link_documento: Optional[str] = None


class MonitoramentoItem(MonitoramentoBase):
    id: int
    created_at: Optional[str] = None


# --- ACOMPANHAMENTO PLANO PRODUTIVO (PLANILHA DINÂMICA) ---
class PlanoProdutivoColunaCreate(BaseModel):
    chave_coluna: str
    titulo_coluna: str
    tipo_coluna: Optional[str] = "texto"
    ordem: Optional[int] = 0

class PlanoProdutivoSalvarCelula(BaseModel):
    linha_id: int
    campo: str # 'status_parcela_1', 'status_parcela_2', 'observacoes', ou chave dinâmica
    valor: Any

class PlanoProdutivoLinhaCreate(BaseModel):
    beneficiario_id: Optional[int] = None
    nome_beneficiario: str
    municipio: Optional[str] = None
    comunidade: Optional[str] = None
    status_parcela_1: Optional[str] = "Pendente"
    status_parcela_2: Optional[str] = "Pendente"
    observacoes: Optional[str] = None
    campos_dinamicos: Optional[Dict[str, Any]] = {}


# --- COTAÇÕES P1+2 ---
class CotacaoP12ItemBase(BaseModel):
    item_nome: Optional[str] = None
    descricao_item: Optional[str] = None
    unidade: Optional[str] = "UN"
    quantidade: float = 1.0
    valor_unitario_estimado: Optional[float] = 0.0
    valor_total_estimado: Optional[float] = 0.0
    fornecedor_vencedor: Optional[str] = None
    status: Optional[str] = "Pendente"

    @validator('descricao_item', pre=True, always=True)
    def set_descricao(cls, v, values):
        return v or values.get('item_nome') or 'Item sem descrição'

    @validator('item_nome', pre=True, always=True)
    def set_item_nome(cls, v, values):
        return v or values.get('descricao_item') or 'Item sem descrição'

class CotacaoP12MasterBase(BaseModel):
    codigo_cotacao: str
    titulo: str
    descricao: Optional[str] = None
    categoria: Optional[str] = "Materiais"
    status: Optional[str] = "Aberta"
    prazo_limite: Optional[str] = None


class CotacaoP12MasterCreate(CotacaoP12MasterBase):
    itens: Optional[List[CotacaoP12ItemBase]] = []

class CotacaoP12MasterUpdate(BaseModel):
    codigo_cotacao: Optional[str] = None
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    status: Optional[str] = None
    prazo_limite: Optional[str] = None
    itens: Optional[List[CotacaoP12ItemBase]] = None

class CotacaoP12Master(CotacaoP12MasterBase):
    id: int
    data_abertura: Optional[str] = None
    data_fechamento: Optional[str] = None
    itens: Optional[List[Dict[str, Any]]] = []



# --- DOCUMENTOS P1+2 ---
class DocumentoP12Base(BaseModel):
    nome_documento: str
    categoria: Optional[str] = "Geral"
    nome_arquivo: str
    caminho_arquivo: str
    tamanho_bytes: Optional[int] = 0

class DocumentoP12(DocumentoP12Base):
    id: int
    data_upload: Optional[str] = None


# --- CRONOGRAMA E PLANEJAMENTO P1+2 ---
class CronogramaP12ItemBase(BaseModel):
    municipio: str
    semana_referencia: int = 1
    ano: int = 2026
    meta_planejada: int = 0
    qtd_executada: int = 0
    status: Optional[str] = "Em Andamento"
    observacoes: Optional[str] = None

class CronogramaP12ItemUpdate(BaseModel):
    meta_planejada: Optional[int] = None
    qtd_executada: Optional[int] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

class CronogramaP12Item(CronogramaP12ItemBase):
    id: int
    updated_at: Optional[str] = None