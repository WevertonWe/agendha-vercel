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

async def extrair_dados_proposta(file_content: bytes, mime_type: str) -> str:
    """
    Analisa uma proposta/orçamento e extrai dados estruturados via Gemini.
    """
    client = get_gemini_client()
    if not client:
        return json.dumps({"erro": "Configuração da API inválida"})

    nome_modelo = "gemini-2.5-flash" 
    
    prompt = """
    Analise este documento de orçamento/proposta comercial.
    Extraia os seguintes dados e retorne APENAS um JSON válido (sem markdown, sem ```json):
    
    1. "valor_total": Valor total da proposta (float, use ponto para decimais). Ex: 1500.50
    2. "data_proposta": Data da proposta no formato YYYY-MM-DD. Se não achar, tente a data atual ou null.
    3. "nome_fornecedor": Nome da empresa fornecedora (string).
    4. "cnpj_fornecedor": CNPJ se houver (string formatada ou limpa).
    5. "resumo_itens": Um resumo curto dos itens cotados para colocar em observação (string).
    6. "numero_cotacao": Se houver referência a um número de cotação/solicitação (Ex: "001", "001/2025", "Nº 123"), extraia como string.
    7. "itens": Lista de itens encontrados com: { "descricao": string, "quantidade": float, "valor_unitario": float, "valor_total": float }. Se não for claro, retorne lista vazia.
    
    Se não encontrar algum dado, retorne null ou string vazia.
    """

    import time 
    max_retries = 2
    last_error = None

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt+1}/{max_retries} com modelo: {nome_modelo}")
            
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
            logger.warning(f"Erro na tentativa {attempt+1}: {error_str}")

            if ("429" in error_str or "quota" in error_str or "resource exhausted" in error_str) and attempt < max_retries - 1:
                logger.warning("Rate Limit detectado. Aguardando 5s...")
                time.sleep(5)
                continue
            
            break

    return json.dumps({"erro": "Falha na análise IA.", "details": f"Modelo {nome_modelo} falhou após tentativas. Erro: {str(last_error)}"})
