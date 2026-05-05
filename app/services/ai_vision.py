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
    client = get_gemini_client()
    if not client:
        return json.dumps({"erro": "Configuração da API inválida"})

    # Lista de Modelos: Emergência/Resiliência (Prioridade 2025)
    modelos_para_tentar = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
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

    # Prompt Otimizado para Estruturação
    prompt = """
    Analise este documento de cadastro.
    Extraia os dados e retorne APENAS um JSON válido seguindo o schema.
    Campos: 'nome_completo', 'sexo', 'data_nascimento', 'cpf', 'escolaridade', 'comunidade', 'municipio', 'estado_uf', 'nis'.
    Se ilegível, retorne "".
    """

    # Loop de Fallback Resiliente (Handshake 2025)
    for nome_modelo in modelos_para_tentar:
        logger.info(f"Tentando processamento com modelo: {nome_modelo}...")
        
        try:
            # Encapsulamento em Part para a nova SDK
            part_arquivo = types.Part.from_bytes(
                data=file_bytes,
                mime_type=mime_type,
            )
            
            response = await asyncio.to_thread(
                client.models.generate_content,
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
            
            # Protocolo de Espera Resiliente (5s) antes do próximo modelo
            if nome_modelo != modelos_para_tentar[-1]:
                logger.info("Aguardando 5s para fallback de modelo...")
                await asyncio.sleep(5)
            continue

    # Em caso de falha total
    return json.dumps({
        "nome_completo": "ERRO DE COTA/MODELO",
        "cpf": "Tente novamente mais tarde",
        "obs": f"Todos os modelos falharam. Último erro: {ultimo_erro}"
    })
