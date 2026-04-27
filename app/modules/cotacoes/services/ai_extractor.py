
import google.generativeai as genai
import json
import os
import logging
import asyncio
from dotenv import load_dotenv

# Reusing configuration if possible, or re-implementing
load_dotenv()
logger = logging.getLogger(__name__)

def configure_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

async def extrair_dados_proposta(file_content: bytes, mime_type: str) -> str:
    """
    Analisa uma proposta/orçamento e extrai dados estruturados via Gemini.
    """
    if not configure_gemini():
        return json.dumps({"erro": "Configuração da API inválida"})

    # --- Configuração Simplificada (One Model Strategy) ---
    # Usamos o modelo mais estável/rápido definido.
    nome_modelo = "gemini-flash-latest" 
    
    dados_arquivo = {"mime_type": mime_type, "data": file_content}
    
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
            model = genai.GenerativeModel(nome_modelo)
            response = await asyncio.to_thread(model.generate_content, [prompt, dados_arquivo])
            
            texto = response.text.replace("```json", "").replace("```", "").strip()
            if "{" in texto:
                start = texto.find("{")
                end = texto.rfind("}") + 1
                texto = texto[start:end]
            
            return texto

        except Exception as e:
            last_error = e
            error_str = str(e)
            logger.warning(f"Erro na tentativa {attempt+1}: {error_str}")

            # Se for Rate Limit (429), espera e tenta de novo (apenas 1 retry extra)
            if ("429" in error_str or "quota" in error_str.lower() or "resource exhausted" in error_str.lower()) and attempt < max_retries - 1:
                logger.warning("Rate Limit detectado. Aguardando 5s...")
                time.sleep(5)
                continue
            
            # Se for outro erro ou acabou as tentativas, sai do loop
            break



    return json.dumps({"erro": "Falha na análise IA.", "details": f"Modelo {nome_modelo} falhou após tentativas. Erro: {str(last_error)}"})
