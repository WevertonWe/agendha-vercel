from google import genai
from google.genai import types
import json
import os
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# --- Schema Pydantic para Estruturação da IA ---
class BeneficiarioExtraido(BaseModel):
    nome_completo: str | None = Field(description="Nome completo do beneficiário")
    sexo: str | None = Field(description="Sexo (Ex: Masculino, Feminino)")
    data_nascimento: str | None = Field(description="Data de Nascimento formato DD/MM/AAAA")
    cpf: str | None = Field(description="CPF com pontuação")
    escolaridade: str | None = Field(description="Escolaridade")
    comunidade: str | None = Field(description="Comunidade onde reside")
    municipio: str | None = Field(description="Município da residência")
    estado_uf: str | None = Field(description="Estado UF (Sigla 2 letras)")
    nis: str | None = Field(description="Número NIS (se houver)")

class AtividadeExtraida(BaseModel):
    nome_atividade: str = Field(description="O nome da atividade marcada com o X")

# --- Configuração Inicial ---
load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    else:
        print("⚠️ AVISO: GOOGLE_API_KEY não encontrada no .env")
        return None

print("--- INICIANDO AI VISION ---")
try:
    client = get_gemini_client()
    if client:
        print("SDK google.genai configurado com sucesso.")
except Exception as e:
    print(f"⚠️ Erro ao configurar genai: {e}")
print("---------------------------")

async def processar_imagem_gemini(caminho_arquivo: str) -> str:
    """
    Envia um arquivo (PDF ou Imagem) para o Gemini e retorna apenas o JSON extraído.
    Implementa Smart Retry (Backoff 30s) e Fallback de modelos para Free Tier.
    """
    global client
    if not client:
        client = get_gemini_client()
    if not client:
        return json.dumps({"erro": "Configuração da API inválida"})

    # Lista de Modelos: Emergência/Resiliência (Prioridade 2025)
    modelos_para_tentar = [
        "gemini-2.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro"
    ]
    ultimo_erro = ""

    caminho = Path(caminho_arquivo)
    if not caminho.exists():
        return json.dumps({"erro": "Arquivo não encontrado"})
        
    try:
        def read_file_content():
            with open(caminho, "rb") as f:
                return f.read()
        
        file_bytes = await asyncio.to_thread(read_file_content)
        mime_type = "application/pdf" if caminho.suffix.lower() == ".pdf" else "image/jpeg"
        
    except Exception as e:
        return json.dumps({"erro": f"Erro ao ler arquivo: {str(e)}"})

    prompt = """
    Analise este documento de cadastro.
    Extraia os dados e retorne APENAS um JSON válido seguindo o schema.
    Campos: 'nome_completo', 'sexo', 'data_nascimento', 'cpf', 'escolaridade', 'comunidade', 'municipio', 'estado_uf', 'nis'.
    Se ilegível, retorne "".
    """

    for nome_modelo in modelos_para_tentar:
        logger.info(f"Tentando processamento com modelo: {nome_modelo}...")
        try:
            part_arquivo = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            response = await client.aio.models.generate_content(
                model=nome_modelo,
                contents=[prompt, part_arquivo],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=BeneficiarioExtraido,
                )
            )
            texto_limpo = response.text
            logger.info(f"✅ SUCESSO com {nome_modelo}")
            return texto_limpo
        except Exception as e:
            logger.warning(f"⚠️ Falha no modelo {nome_modelo}: {e}")
            ultimo_erro = str(e)
            if nome_modelo != modelos_para_tentar[-1]:
                logger.info("Aguardando 5s para fallback de modelo...")
                await asyncio.sleep(5)
            continue

    return json.dumps({
        "nome_completo": "ERRO DE COTA/MODELO",
        "cpf": "Tente novamente mais tarde",
        "obs": f"Todos os modelos falharam. Último erro: {ultimo_erro}"
    })


async def identificar_tipo_atividade_gemini(file_bytes: bytes, filename: str) -> str:
    """
    Recebe os bytes de um PDF ou JPEG escaneado e identifica o tipo de atividade marcado na folha.
    Usa o fallback de modelos resiliente.
    """
    global client
    if not client:
        client = get_gemini_client()
    if not client:
        return "DOCUMENTO_SEM_IA"

    modelos_para_tentar = [
        "gemini-2.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro"
    ]
    ultimo_erro = ""
    
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    mime_type = "application/pdf" if ext == "pdf" else "image/jpeg"

    prompt = """
    Você é um especialista em OCR e Análise de Documentos.
    O documento enviado contém uma seção chamada 'TIPO DE ATIVIDADE'.
    Abaixo desta seção, há várias opções com caixas de seleção (checkboxes) ou quadrados.
    Existe apenas UMA (ou mais de uma, dependendo do erro de preenchimento, mas foque na principal) opção marcada com um 'x', um traço, ou preenchida.
    
    Identifique a opção que está MARCADA e retorne SOMENTE o nome da atividade correspondente.
    Exemplo de opções: 'Levantamento socioeconômico e geolocalização', 'Cadastro do Grupo Familiar', 'Caracterização da UPF I', 'Visita Técnica', etc.
    
    Importante: Limpe a string, remova o texto entre parênteses se possível e retorne algo curto e claro. Por exemplo: 'Visita Técnica' ou 'Caracterização da UPF I'.
    """

    for nome_modelo in modelos_para_tentar:
        logger.info(f"Tentando processamento de Atividade com modelo: {nome_modelo}...")
        try:
            part_arquivo = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            response = await client.aio.models.generate_content(
                model=nome_modelo,
                contents=[prompt, part_arquivo],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AtividadeExtraida,
                    temperature=0.0
                )
            )
            
            try:
                dados = json.loads(response.text)
                atividade = dados.get("nome_atividade")
                if atividade and atividade.strip():
                    logger.info(f"✅ SUCESSO com {nome_modelo}: Atividade encontrada -> {atividade}")
                    return atividade.strip().upper()
            except Exception as j_err:
                logger.warning(f"Erro no JSON parse: {j_err}")
                pass
                
        except Exception as e:
            err_msg = str(e)
            logger.warning(f"⚠️ Falha no modelo {nome_modelo} ao extrair atividade: {e}")
            ultimo_erro = err_msg
            
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "Quota" in err_msg:
                logger.warning("Limite de Cota Atingido (429)! Tentando próximo modelo sem longa espera...")
                await asyncio.sleep(2)
            else:
                if nome_modelo != modelos_para_tentar[-1]:
                    logger.info("Aguardando 3s para fallback de modelo...")
                    await asyncio.sleep(3)
            continue

    logger.error(f"Todos os modelos falharam na leitura de Atividade. Último erro: {ultimo_erro}")
    return "DOCUMENTO"
