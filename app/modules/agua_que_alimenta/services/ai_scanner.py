from google import genai
from google.genai import types
import json
import os
import logging
import asyncio
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def get_gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return None

async def extrair_lista_presenca(file_content: bytes, mime_type: str) -> str:
    """
    Analisa uma Lista de Presença ou documento similar e extrai nomes e CPFs via Gemini.
    
    - Configura API Key do Google.
    - Envia prompt específico para OCR de listas.
    - Trata rechamada (retries) em caso de erro 429 (Quota).
    - Limpa e retorna o JSON bruto da resposta.
    """
    client = get_gemini_client()
    if not client:
        return json.dumps({"erro": "Configuração da API inválida"})

    nome_modelo = "gemini-2.5-flash" 
    
    prompt = """
    Analise este documento (Lista de Presença, Assinatura ou Cadastro).
    Extraia uma lista de beneficiários identificados.
    
    Retorne APENAS um JSON válido (sem markdown, sem ```json) com a seguinte estrutura:
    {
        "tipo_documento": "Lista de Presença" | "Outro",
        "data_evento": "YYYY-MM-DD" (ou null se não encontrar),
        "beneficiarios_detectados": [
            {
                "nome_extraido": "Nome encontrado (em maiúsculas)",
                "cpf_extraido": "CPF se houver (formato 000.000.000-00 ou limpo)",
                "linha_original": "Texto da linha onde foi encontrado para conferência"
            }
        ]
    }
    Se a lista for longa, extraia todos que conseguir.
    """

    import time 
    max_retries = 2
    last_error = None

    for attempt in range(max_retries):
        try:
            logger.info(f"GRH Scan: Tentativa {attempt+1}/{max_retries} com modelo: {nome_modelo}")
            part_arquivo = types.Part.from_bytes(data=file_content, mime_type=mime_type)
            
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=nome_modelo,
                contents=[prompt, part_arquivo],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            texto = response.text.replace("```json", "").replace("```", "").strip()
            if "{" in texto:
                start = texto.find("{")
                end = texto.rfind("}") + 1
                texto = texto[start:end]
            
            return texto

        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            logger.warning(f"Erro na tentativa {attempt+1}: {e}")

            if ("429" in error_str or "quota" in error_str) and attempt < max_retries - 1:
                time.sleep(5)
                continue
            
            break

    return json.dumps({"erro": "Falha na análise IA.", "details": str(last_error)})
