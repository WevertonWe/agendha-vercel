from google import genai
from google.genai import types
import json
import os
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google.api_core import exceptions as google_exceptions

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

    # Lista de modelos Free Tier (Ajustada para cota real do usuário)
    modelos_para_tentar = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-3-flash", "gemini-2.5-flash"]
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
        dados_arquivo = {"mime_type": mime_type, "data": file_bytes}
        
    except Exception as e:
        return json.dumps({"erro": f"Erro ao ler arquivo: {str(e)}"})

    # Prompt Otimizado
    prompt = """
    Analise este documento de cadastro.
    Extraia os dados e retorne APENAS um JSON válido.
    Campos obrigatórios: 'nome_completo', 'sexo', 'data_nascimento', 'cpf', 'escolaridade', 'comunidade', 'municipio', 'estado_uf', 'nis'.
    Se o campo estiver vazio ou ilegível, retorne string vazia "".
    NÃO USE MARKDOWN. NÃO USE ```json. Retorne apenas o texto do JSON cru.
    """

    # Loop de Fallback entre Modelos
    for nome_modelo in modelos_para_tentar:
        print(f"Buscando modelo: {nome_modelo}...")
        model = genai.GenerativeModel(nome_modelo)
        
        # Loop Interno de Smart Retry (Max 2 retentativas por modelo)
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                # Na nova API, enviamos os bytes encapsulados em Part
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
                print(f"✅ SUCESSO com {nome_modelo}")
                
                # --- RATE LIMIT PREVENTIVO (Respeitar 5 RPM -> 12s delay) ---
                await asyncio.sleep(12) 
                
                return texto_limpo

            except google_exceptions.ResourceExhausted:
                # Erro 429: Quota Exceeded
                msg = f"⚠️ Rate limit (429) atingido no modelo {nome_modelo}. "
                if attempt < max_retries:
                    logger.warning(f"{msg} Pausando 30s antes da tentativa {attempt + 2}/{max_retries + 1}...")
                    await asyncio.sleep(30)
                    continue # Tenta o MESMO modelo novamente
                else:
                    logger.error(f"{msg} Máximo de retentativas atingido. Pulando para fallback...")
                    break # Sai do loop de retry e tenta o próximo modelo

            except Exception as e:
                print(f"⚠️ Falha técnica no modelo {nome_modelo}: {e}")
                ultimo_erro = str(e)
                break # Erro não relacionado à cota (ex: schema), tenta próximo modelo

    # Em caso de falha total
    return json.dumps({
        "nome_completo": "ERRO DE COTA/MODELO",
        "cpf": "Tente novamente mais tarde",
        "obs": f"Todos os modelos falharam. Último erro: {ultimo_erro}"
    })
