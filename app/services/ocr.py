import logging
import asyncio
from typing import Dict, Any
from app.config import settings
import json
from app.services import ai_vision

# ==============================================================================
# CONFIGURAÇÕES DE OCR (ROIs) - Mantido para compatibilidade, mesmo usando Gemini
# ==============================================================================
LARGURA_PADRAO = 1000

RETANGULO_PRINCIPAL_PAG1_COORDS = {"x": 10, "y": 10, "w": 980, "h": 300}

ROI_DEFINICOES_PAGINA1 = {
    "nome_completo_l1": {"x": 175, "y": 11, "w": 760, "h": 32, "tipo": "texto"},
    "nome_completo_l2": {"x": 6, "y": 45, "w": 502, "h": 32, "tipo": "texto"},
    "data_nascimento":  {"x": 207, "y": 75, "w": 251, "h": 30, "tipo": "texto"},
    "cpf":              {"x": 600, "y": 75, "w": 325, "h": 30, "tipo": "texto"},
    "sexo_cb_masc":     {"x": 725, "y": 53, "w": 25, "h": 25, "tipo": "checkbox", "campo_destino": "sexo", "valor_marcado": "Masculino"},
    "sexo_cb_fem":      {"x": 870, "y": 53, "w": 25, "h": 25, "tipo": "checkbox", "campo_destino": "sexo", "valor_marcado": "Feminino"},
    "escolaridade_cb_analfabeto":   {"x": 281, "y": 116, "w": 25, "h": 18, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Analfabeto"},
    "escolaridade_cb_sabe_ler":     {"x": 402, "y": 115, "w": 30, "h": 19, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Sabe ler e escrever"},
    "escolaridade_cb_fund_4":       {"x": 600, "y": 115, "w": 23, "h": 19, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Fundamental - até a 4ª série"},
    "escolaridade_cb_fund_8":       {"x": 13, "y": 150, "w": 24, "h": 19, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Fundamental - de 5ª a 8ª série"},
    "escolaridade_cb_medio_inc":    {"x": 353, "y": 150, "w": 27, "h": 17, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Médio - Incompleto"},
    "escolaridade_cb_medio_comp":   {"x": 600, "y": 145, "w": 25, "h": 22, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Médio - Completo"},
    "escolaridade_cb_sup_inc":      {"x": 10, "y": 185, "w": 27, "h": 15, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Superior - Incompleto"},
    "escolaridade_cb_sup_comp":     {"x": 353, "y": 183, "w": 27, "h": 17, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Superior - Completo"},
    "comunidade":       {"x": 157, "y": 209, "w": 764, "h": 24, "tipo": "texto"},
    "ref_localizacao":  {"x": 267, "y": 244, "w": 648, "h": 16, "tipo": "texto"},
    "municipio":        {"x": 129, "y": 273, "w": 594, "h": 27, "tipo": "texto"},
    "estado_uf":        {"x": 863, "y": 278, "w": 59,  "h": 22, "tipo": "texto"}
}

ROI_DEFINICOES_PAGINA2 = {
    "nis": {"x": 300, "y": 540, "w": 173, "h": 16, "tipo": "texto"},
}

TODAS_ROIS_POR_PAGINA = {
    1: {
        "retangulo_principal": RETANGULO_PRINCIPAL_PAG1_COORDS,
        "campos": ROI_DEFINICOES_PAGINA1
    },
    2: {
        "retangulo_principal": None,
        "campos": ROI_DEFINICOES_PAGINA2
    },
}

async def processar_ocr_completo(file_path: str) -> Dict[str, Any]:
    """
    Função principal: orquestra o processo de OCR usando Google Gemini Flash.
    Suporta PDF e Imagens nativamente via API do Gemini.
    As funções locais (Tesseract/OpenCV) foram removidas para poupar memória na Vercel.
    """
    try:
        # Passa o caminho do arquivo diretamente para o serviço de visão
        result = await ai_vision.processar_imagem_gemini(file_path)
        
        full_text = ""
        structured_data = {}
        
        clean_result = result.strip()
        if clean_result.startswith("```json"):
            clean_result = clean_result.replace("```json", "").replace("```", "").strip()
        
        try:
            page_data = json.loads(clean_result)
            if isinstance(page_data, dict):
                structured_data.update(page_data)
        except json.JSONDecodeError:
            full_text = result

        if structured_data:
            return structured_data
            
        return {"texto_bruto": full_text}

    except Exception as e:
        logging.error(f"Erro no OCR Gemini: {e}")
        raise e
